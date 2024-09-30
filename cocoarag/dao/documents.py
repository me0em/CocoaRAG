# document.py
import redis
from entities.documents import Document

class DocumentDAO:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

    def add_document(self, document: Document):
        self.redis_client.set(document.id, document.content)
