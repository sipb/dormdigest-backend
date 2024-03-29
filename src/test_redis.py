from redis import StrictRedis
from redis_cache import RedisCache
import time

client = StrictRedis(host="localhost", decode_responses=True)
cache = RedisCache(redis_client=client)

GARBAGE = 1

def do_stuff(a,b):
    @cache.cache(ttl=60, limit=10)
    def do_stuff_helper(a):
        time.sleep(1)
        return [a]

start_time = time.time()
for i in range(5):
    do_stuff(i,GARBAGE)
print(time.time()-start_time)
    
start_time = time.time()
for i in range(10):
    do_stuff(i, GARBAGE)
print(time.time()-start_time)

