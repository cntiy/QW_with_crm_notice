import json
import os
import redis
from dotenv import load_dotenv

load_dotenv()

_redis = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    password=os.getenv("REDIS_PASSWORD") or None,
    decode_responses=True,
)

_KEY = "crm:leads:today"


def save_leads(leads: list[dict]) -> None:
    _redis.set(_KEY, json.dumps(leads, ensure_ascii=False))


def get_leads() -> list[dict]:
    raw = _redis.get(_KEY)
    return json.loads(raw) if raw else []


def clear_leads() -> None:
    _redis.delete(_KEY)
