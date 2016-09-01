import socket
import traceback

from aiohttp.web_exceptions import HTTPException
from chilero.web import JSONResponse

from unified.config import CORS_ALLOWED_ORIGIN


async def cors_middleware(app, handler):

    async def middleware(request):
        resp = await handler(request)
        resp.headers['Access-Control-Allow-Origin'] = CORS_ALLOWED_ORIGIN
        return resp

    return middleware


async def wrap_errors_middleware(app, handler):

    async def middleware(request):
        def _wrap(e):
            status = getattr(e, 'status', 500)
            return JSONResponse(
                dict(
                    message=str(e),
                    stacktrace=traceback.format_exc().splitlines(),
                    hostname=socket.getfqdn()
                ),
                status=status
            )

        try:
            resp = await handler(request)
        except HTTPException as e:
            resp = _wrap(e)
        except Exception as e:
            resp = _wrap(e)

        return resp

    return middleware
