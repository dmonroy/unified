from chilero import web

from unified.middlewares import cors_middleware, wrap_errors_middleware
from unified.resources import Nodes

def main():
    web.run(
        web.Application,
        routes=[
            ['/', Nodes]
        ],
        middlewares=[
            cors_middleware,
            wrap_errors_middleware
        ]
    )


if __name__ == '__main__':
    main()
