from slowapi import Limiter
from slowapi.util import get_remote_address
import os

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0") #busca variable de entorno

limiter = Limiter(key_func=get_remote_address, storage_uri=redis_url)