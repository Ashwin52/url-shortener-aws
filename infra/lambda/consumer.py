import json
import boto3
from datetime import datetime

s3 = boto3.client('s3', region_name='ap-south-1')
BUCKET = "url-shortener-analytics-ashwin"

def handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        
        short_code = body.get('short_code')
        timestamp = body.get('timestamp')
        
        dt = datetime.utcfromtimestamp(timestamp)
        s3_key = f"clicks/year={dt.year}/month={dt.month:02d}/day={dt.day:02d}/{short_code}-{timestamp}.json"
        
        s3.put_object(
            Bucket=BUCKET,
            Key=s3_key,
            Body=json.dumps(body),
            ContentType='application/json'
        )
        
        print(f"Saved click event: {s3_key}")
    
    return {"statusCode": 200}
