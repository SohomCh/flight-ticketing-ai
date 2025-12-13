from app.core.redis import redis_client

print(redis_client.ping())
