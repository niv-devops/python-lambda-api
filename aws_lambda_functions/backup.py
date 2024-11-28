import boto3
from datetime import datetime
import os

s3 = boto3.client('s3')

SOURCE_PREFIX = "files_to_backup/"
BACKUP_PREFIX = "backups/"
DATE_FORMAT = "%d-%m-%Y"

def list_files_in_prefix(bucket_name, prefix):
    """ List all files in the given bucket and prefix """
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    files = response.get("Contents", [])
    return [file["Key"] for file in files if file["Key"] != prefix]

def backup_files(bucket_name):
    """ Back up files from SOURCE_PREFIX to BACKUP_PREFIX """
    today = datetime.now()
    backup_folder = f"{BACKUP_PREFIX}{today.strftime(DATE_FORMAT)}/"
    
    files_to_backup = list_files_in_prefix(bucket_name, SOURCE_PREFIX)
    if not files_to_backup:
        print(f"No files found in prefix '{SOURCE_PREFIX}' to back up.")
        return
    
    for file_key in files_to_backup:
        file_name = file_key[len(SOURCE_PREFIX):]
        backup_key = f"{backup_folder}{file_name}"

        s3.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': file_key},
            Key=backup_key
        )
        print(f"Backed up '{file_key}' to '{backup_key}'")
    
    print(f"Backup completed for {len(files_to_backup)} files.")

def lambda_handler(event, context):
    bucket_name = "tasty-kfc-bucket"
    backup_files(bucket_name)


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