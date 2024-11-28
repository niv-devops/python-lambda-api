import boto3
import os
import csv
from xlsxwriter.workbook import Workbook

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    download_path = f"/tmp/{os.path.basename(object_key)}"
    upload_path = f"/tmp/{os.path.splitext(os.path.basename(object_key))[0]}.xlsx"
    
    s3.download_file(bucket_name, object_key, download_path)
    
    workbook = Workbook(upload_path)
    worksheet = workbook.add_worksheet()
    
    with open(download_path, 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    workbook.close()
    
    converted_key = f"converted/{os.path.splitext(os.path.basename(object_key))[0]}.xlsx"
    s3.upload_file(upload_path, bucket_name, converted_key)
    
    return {
        "statusCode": 200,
        "body": f"Successfully converted {object_key} to {converted_key}"
    }


""" Test Event:
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "tasty-kfc-bucket"
        },
        "object": {
          "key": "csv/sample.csv"
        }
      }
    }
  ]
}
"""