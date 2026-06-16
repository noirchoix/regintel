from redis import Redis
from rq import Queue

from app.core.config import settings


def get_queue(name: str = 'regintel') -> Queue:
    connection = Redis.from_url(settings.redis_url)
    return Queue(name, connection=connection, default_timeout=900)
