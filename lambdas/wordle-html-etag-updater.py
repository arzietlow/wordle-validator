import hashlib
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get the S3 bucket and key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Calculate the MD5 hash of the object's contents
    object_data = s3.get_object(Bucket=bucket_name, Key=object_key)['Body'].read()
    object_hash = hashlib.md5(object_data).hexdigest()

    # Set the ETag of the object as a metadata property
    result = s3.copy_object(
        Bucket=bucket_name,
        CopySource={'Bucket': bucket_name, 'Key': object_key},
        Key=object_key,
        Metadata={'ETag': object_hash},
        MetadataDirective='REPLACE',
        ContentType='text/html'
    )
