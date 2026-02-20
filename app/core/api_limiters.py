from fastapi import Request
from .database.services import TokenService
from typing import List
from pyrate_limiter import (
    RedisBucket,
    Limiter,
    Rate,
    Duration,
    BucketFactory,
    AbstractBucket,
    RateItem,
)
from pyrate_limiter.buckets.redis_bucket import LuaScript
from redis.asyncio import Redis
from time import time_ns

async def get_user_id(request: Request):
    if token := request.session.get("access_token"):
        try:
            payload = TokenService.decode(token)
            if user_id := payload.get("sub"):
                return user_id
        except Exception:
            pass

    return request.client.host


text_limiter: Limiter = None
docs_limiter: Limiter = None





class UserBucketFactory(BucketFactory):
    def __init__(
        self,
        redis: Redis,
        rates: List[Rate],
        bucket_prefix: str,
        script_hash: str,
    ):
        self.redis = redis
        self.rates = rates
        self.bucket_prefix = bucket_prefix
        self.script_hash = script_hash

    def wrap_item(self, name: str, weight: int = 1):
        # We need this method because BucketFactory requires it.
        # It's used by Limiter to wrap the key (name) into a RateItem.
        now = time_ns() // 1000000
        return RateItem(name, now, weight=weight)

    def get(self, item: RateItem) -> AbstractBucket:
        # Construct a unique bucket key for this user
        bucket_key = f"{self.bucket_prefix}:{item.name}"
        return RedisBucket(
            rates=self.rates,
            redis=self.redis,
            bucket_key=bucket_key,
            script_hash=self.script_hash,
        )


async def init_limiters(redis: Redis):
    global text_limiter, docs_limiter

    # Pre-load the Lua script for RedisBucket
    script_hash = await redis.script_load(LuaScript.PUT_ITEM)

    text_factory = UserBucketFactory(
        redis, [Rate(1, Duration.MINUTE)], "bucket:text-generation", script_hash
    )
    docs_factory = UserBucketFactory(
        redis, [Rate(5, Duration.MINUTE)], "bucket:docs-ingestion", script_hash
    )

    text_limiter = Limiter(text_factory)
    docs_limiter = Limiter(docs_factory)
