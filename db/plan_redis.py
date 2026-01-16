from redis.asyncio import Redis  # redis-py의 async 클라이언트
import json
# Redis 설정 (로컬 개발 기준, 프로덕션에서는 환경변수로 관리)
REDIS_URL = "redis://localhost:6379"
redis_con = None

async def preload_redis():
    try:
        global redis_con
        redis_con = Redis.from_url(url=REDIS_URL, decode_responses=True)
        # decode_responses=True --> 바이트스트림으로 도착한 데이터 utf-8로 자동으로 변환

        print(f"{REDIS_URL}로 Redis서버 미리 연결됨.")
    except Exception as e:
        print(f"모델 preload 실패 또는 Redis연결 실패 : {e}")


async def redis_insert(user_id, answer):
        print("redis_con >> " , redis_con)
        await redis_con.rpush(user_id, json.dumps(answer))

