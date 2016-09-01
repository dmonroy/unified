from aiohttp.web_exceptions import HTTPException
from aiohttp.web_reqrep import Response


class HTTPException(HTTPException):
    empty_body = False

    def __init__(self, *, status=None, headers=None, reason=None,
                 body=None, text=None, content_type=None):
        self.status_code = status
        Response.__init__(self, status=self.status_code,
                          headers=headers, reason=reason,
                          body=body, text=text, content_type=content_type)
        Exception.__init__(self, self.reason)
        if self.body is None and not self.empty_body:
            self.text = "{}: {}".format(self.status, self.reason)
