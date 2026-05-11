from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import random
import string

app = FastAPI()

# DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('url-shortener')

# Base62 character set
BASE62 = string.ascii_letters + string.digits

def generate_short_code(length=6):
    return ''.join(random.choices(BASE62, k=length))

# Request model
class URLRequest(BaseModel):
    long_url: str

# POST /shorten
@app.post("/shorten")
def shorten_url(request: URLRequest):
    for _ in range(5):
        code = generate_short_code()
        try:
            table.put_item(
                Item={
                    'short_code': code,
                    'long_url': request.long_url,
                },
                ConditionExpression='attribute_not_exists(short_code)'
            )
            return {
                "short_code": code,
                "short_url": f"http://localhost:8000/{code}",
                "long_url": request.long_url
            }
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            continue

    raise HTTPException(status_code=500, detail="Could not generate unique code")

# GET /{code}
@app.get("/{code}")
def redirect_url(code: str):
    response = table.get_item(Key={'short_code': code})

    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="URL not found")

    return {
        "long_url": response['Item']['long_url'],
        "short_code": code
    }
