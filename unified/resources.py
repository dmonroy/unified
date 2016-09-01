from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_reqrep import StreamResponse
from chilero import web
from chilero.web import JSONResponse

from .config import DOCKER_HOSTS
from .exceptions import HTTPException


class DockerClient(object):
    _session = None
    @classmethod
    def session(cls):
        if cls._session is None:
            cls._session = ClientSession()
        return cls._session

    async def api_get(self, node, uri):
        if node not in DOCKER_HOSTS:
            raise HTTPNotFound()

        url = 'http://{}{}'.format(DOCKER_HOSTS[node], uri)
        async with self.session().get(url) as resp:
            if resp.status >= 400:
                text = await resp.text()
                raise HTTPException(status=resp.status, text=text)

            json_resp = await resp.json()

        return json_resp


class BaseResource(web.Resource, DockerClient):
    pass


class StreamView(web.View, DockerClient):
    async def get_url(self, *args, **kwargs):
        raise NotImplementedError()

    async def get(self, *args, **kwargs):
        url = await self.get_url(*args, **kwargs)

        async with self.session().get(url) as r:
            resp = StreamResponse(
                status=200,
                reason='OK',
                headers={'Content-Type': 'text/plain'}
            )

            await resp.prepare(self.request)

            while True:
                chunk = await r.content.read(128)
                if not chunk:
                    break
                resp.write(chunk)


class NodeEvents(StreamView):

    async def get_url(self, nodes_id):
        return 'http://{}/events'.format(DOCKER_HOSTS[nodes_id])


class ContainerLogs(StreamView):

    async def get_url(self, nodes_id, containers_id):
        return 'http://{}/containers/{}/logs?stderr=1&stdout=1&timestamps=1' \
              '&follow=1&tail=10'.format(DOCKER_HOSTS[nodes_id], containers_id)


class ContainerStats(StreamView):

    async def get_url(self, nodes_id, containers_id):
        return 'http://{}/containers/{}/stats'.format(
            DOCKER_HOSTS[nodes_id], containers_id
        )


class ContainerTop(web.View, DockerClient):

    async def get(self, nodes_id, containers_id):
        uri = '/containers/{}/top?ps_args=aux'.format(containers_id)
        top = await self.api_get(nodes_id, uri)
        return JSONResponse(top)


class Containers(BaseResource):

    nested_entity_resources = dict(
        logs=ContainerLogs,
        top=ContainerTop,
        stats=ContainerStats,
    )

    async def index(self, nodes_id):
        uri = '/containers/json'.format(DOCKER_HOSTS[nodes_id])
        j = await self.api_get(nodes_id, uri)
        containers = []
        for obj in j:
            containers.append(dict(
                url=self.get_object_url(obj['Id']),
                id=obj['Id'],
                Image=obj['Image'],
                Names=obj['Names'],
                State=obj['State'],
                Status=obj['Status'],
                Created=obj['Created'],
                Labels=obj['Labels'],
            ))
        return self.response(dict(objects=containers))

    async def show(self, nodes_id, id):
        uri = '/containers/{}/json'.format(id)
        body = await self.api_get(nodes_id, uri)
        return self.response(body=body)

    def default_kwargs_for_urls(self):
        return dict(
            nodes_id=self.request.match_info.get('nodes_id')
        )


class Images(BaseResource):

    async def index(self, nodes_id):
        uri = '/images/json?all=1'
        j = await self.api_get(nodes_id, uri)
        hosts = []
        for h in j:
            h['url'] = self.get_object_url(h['Id'])
            hosts.append(h)
        return self.response(dict(objects=hosts))

    async def show(self, nodes_id, id):
        uri = '/images/{}/json'.format(id)
        body = await self.api_get(nodes_id, uri)
        return self.response(body=body)

    def default_kwargs_for_urls(self):
        return dict(
            nodes_id=self.request.match_info.get('nodes_id')
        )


class Nodes(BaseResource):
    nested_entity_resources = dict(
        containers=Containers,
        images=Images,
        events=NodeEvents,
    )

    def index(self):
        objects = []
        for h in DOCKER_HOSTS.keys():
            objects.append(dict(
                name=h,
                url=self.get_object_url(h)
            ))
        return self.response(dict(objects=objects))

    async def show(self, id):
        uri = '/info'
        body = await self.api_get(id, uri)
        return self.response(body=body)
