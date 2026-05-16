from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import boto3
import random
import string
import time
import json

app = FastAPI()

# DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('url-shortener')
cache_table = dynamodb.Table('url-shortener-cache')

# SQS connection
sqs = boto3.client('sqs', region_name='ap-south-1')
SQS_URL = "https://sqs.ap-south-1.amazonaws.com/517169952624/url-click-events"

# Base62 character set
BASE62 = string.ascii_letters + string.digits

def generate_short_code(length=6):
    return ''.join(random.choices(BASE62, k=length))

# Request model
class URLRequest(BaseModel):
    long_url: str
    expiry_days: int = 30

# ─── Rate Limiter ───────────────────────────────────────
def check_rate_limit(ip: str):
    now = int(time.time())
    window = 60
    max_requests = 10
    key = f"ratelimit#{ip}"
    window_start = now - window

    try:
        response = cache_table.get_item(Key={'short_code': key})
        if 'Item' in response:
            item = response['Item']
            timestamps = item.get('timestamps', [])
            timestamps = [t for t in timestamps if t > window_start]
            if len(timestamps) >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Max 10 requests per minute."
                )
            timestamps.append(now)
        else:
            timestamps = [now]

        cache_table.put_item(Item={
            'short_code': key,
            'timestamps': timestamps,
            'ttl': now + window
        })
    except HTTPException:
        raise
    except Exception:
        pass

# ─── Cache Helpers ──────────────────────────────────────
def get_from_cache(code: str):
    try:
        response = cache_table.get_item(Key={'short_code': code})
        if 'Item' in response:
            return response['Item'].get('long_url')
    except Exception:
        pass
    return None

def save_to_cache(code: str, long_url: str, ttl_seconds: int = 300):
    try:
        cache_table.put_item(Item={
            'short_code': code,
            'long_url': long_url,
            'ttl': int(time.time()) + ttl_seconds
        })
    except Exception:
        pass

# ─── SQS Event ──────────────────────────────────────────
def send_click_event(code: str, long_url: str, ip: str):
    try:
        event = {
            "short_code": code,
            "long_url": long_url,
            "ip": ip,
            "timestamp": int(time.time())
        }
        sqs.send_message(
            QueueUrl=SQS_URL,
            MessageBody=json.dumps(event)
        )
    except Exception:
        pass  # fail open

# ─── Routes ─────────────────────────────────────────────

# POST /shorten
@app.post("/shorten")
def shorten_url(request: URLRequest, req: Request):
    client_ip = req.client.host
    check_rate_limit(client_ip)

    expiry_time = int(time.time()) + (request.expiry_days * 86400)

    for _ in range(5):
        code = generate_short_code()
        try:
            table.put_item(
                Item={
                    'short_code': code,
                    'long_url': request.long_url,
                    'ttl': expiry_time,
                    'created_at': int(time.time())
                },
                ConditionExpression='attribute_not_exists(short_code)'
            )
            return {
                "short_code": code,
                "short_url": f"http://localhost:8000/{code}",
                "long_url": request.long_url,
                "expires_in_days": request.expiry_days
            }
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            continue

    raise HTTPException(status_code=500, detail="Could not generate unique code")

# GET /{code}
@app.get("/{code}")
def redirect_url(code: str, req: Request):
    # 1. Check cache first
    cached = get_from_cache(code)
    if cached:
        send_click_event(code, cached, req.client.host)
        return {
            "long_url": cached,
            "short_code": code,
            "source": "cache"
        }

    # 2. Cache miss — hit DynamoDB
    response = table.get_item(Key={'short_code': code})

    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="URL not found or expired")

    long_url = response['Item']['long_url']

    # 3. Save to cache
    save_to_cache(code, long_url)

    # 4. Send click event to SQS
    send_click_event(code, long_url, req.client.host)

    return {
        "long_url": long_url,
        "short_code": code,
        "source": "database"
    }
