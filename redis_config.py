import redis

# 1. Create ONE central pool when your app starts
# max_connections prevents your app from opening too many connections and crashing Redis
shared_pool = redis.ConnectionPool(
    host='localhost', 
    port=6379, 
    max_connections=50, 
    decode_responses=True
)

# 2. You tell the Redis client to use the shared pool instead of making its own
r = redis.Redis(connection_pool=shared_pool)

print("Redis connection established")
