import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

redis_stream = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
