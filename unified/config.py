import os

CORS_ALLOWED_ORIGIN = os.getenv('CORS_ALLOWED_ORIGIN', '*')
DOCKER_HOSTS = dict(
    [
        x.split('=') for x in
        os.getenv('DOCKER_HOSTS', 'default=localhost:2375').split(',')
    ]
)
