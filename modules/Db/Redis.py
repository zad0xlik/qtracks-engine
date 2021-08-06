import redis
import json

r = redis.Redis(
    host='127.0.0.1',
    port=6379,
    password='otsosika',
    decode_responses=True
)

# r = redis.Redis(
#     host='127.0.0.1',
#     port=6379,
#     decode_responses=True
# )
