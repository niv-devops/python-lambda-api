import json
import boto3
import requests

s3 = boto3.client('s3')
BUCKET_NAME = 'tasty-kfc-bucket'
WIKIPEDIA_FILE_KEY = 'wikipedia.txt'

def lambda_handler(event, context):
    topic = event.get('topic')
    if not topic:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Topic is required'})
        }
    url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{topic}'
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': f'Failed to fetch Wikipedia summary for {topic}.'})
            }
        data = response.json()
        summary = data.get('extract', 'No summary available.')
        try:
            s3_response = s3.get_object(Bucket=BUCKET_NAME, Key=WIKIPEDIA_FILE_KEY)
            existing_content = s3_response['Body'].read().decode('utf-8')
        except s3.exceptions.NoSuchKey:
            existing_content = ''
        updated_content = existing_content + f'\n\n{topic}:\n{summary}'
        s3.put_object(Bucket=BUCKET_NAME, Key=WIKIPEDIA_FILE_KEY, Body=updated_content)
        return {
            "statusCode": 200,
            "body": f"File uploaded to S3 at 's3://{BUCKET_NAME}/{WIKIPEDIA_FILE_KEY}'."   
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error: {str(e)}'})
        }