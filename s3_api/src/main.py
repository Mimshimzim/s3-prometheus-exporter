from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from utils import generate_random_string
from functools import wraps
from config import *
import logging
import uvicorn
import boto3
import time

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=S3_CONFIG,
    verify=False
    )

def s3_operation(api_name):
    def s3_operation_decorator(func):
        @wraps(func)
        def s3_operation_wrapper(*args, **kwargs):
            try:
                start_time = time.perf_counter()
                func(*args, **kwargs)
                taken_time = time.perf_counter() - start_time
                return {"latency": f"{taken_time:.2f}","api":api_name , "endpoint": S3_ENDPOINT}
            except ClientError as e:
                logger.error(f"Error in S3 operation: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        return s3_operation_wrapper
    return s3_operation_decorator



@app.get("/list-s3-buckets")
@s3_operation(api_name="list-s3-buckets")
def list_s3_buckets():
    s3_client.list_buckets()

@app.get("/get-s3-bucket-acl")
@s3_operation(api_name="get-s3-bucket-acl")
def get_s3_bucket_acl():
    s3_client.get_bucket_acl(Bucket=S3_BUCKET_NAME)

@app.get("/list-s3-objects")
@s3_operation(api_name="list-s3-objects")
def get_s3_object():
    s3_client.list_objects(Bucket=S3_BUCKET_NAME)

@app.get("/get-s3-object")
@s3_operation(api_name="get-s3-object")
def get_s3_object():
    s3_client.get_object(Bucket=S3_BUCKET_NAME,Key=S3_OBJECT_NAME)

@app.get("/get-s3-object-tagging")
@s3_operation(api_name="get-s3-object-tagging")
def get_s3_object_tagging():
    s3_client.get_object_tagging(Bucket=S3_BUCKET_NAME,Key=S3_OBJECT_NAME)

@app.get("/put-s3-object")
@s3_operation(api_name="put-s3-object")
def put_s3_object():
    body=generate_random_string(10)
    s3_client.put_object(Bucket=S3_BUCKET_NAME,ACL="public-read",Key=S3_OBJECT_NAME,Body=body)

@app.get("/put-s3-bucket-acl-public")
@s3_operation(api_name="put-s3-bucket-acl-public")
def put_s3_bucket_acl():
    s3_client.put_bucket_acl(Bucket=S3_BUCKET_NAME,ACL="public-read")

@app.get("/put-s3-bucket-acl-private")
@s3_operation(api_name="put-s3-bucket-acl-private")
def put_s3_bucket_acl():
    s3_client.put_bucket_acl(Bucket=S3_BUCKET_NAME,ACL="private")

@app.get("/put-s3-object-tagging")
@s3_operation(api_name="put-s3-object-tagging")
def put_s3_object_tagging():
    s3_client.put_object_tagging(Bucket=S3_BUCKET_NAME,Key=S3_OBJECT_NAME,Tagging=S3_OBJECT_TAGGING_CONFIGURATION)

@app.get("/delete-s3-object")
@s3_operation(api_name="delete-s3-object")
def delete_s3_object():
    s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=S3_OBJECT_NAME)

@app.get("/delete-s3-object-tagging")
@s3_operation(api_name="delete-s3-object-tagging")
def delete_s3_object_tagging():
    s3_client.delete_object_tagging(Bucket=S3_BUCKET_NAME, Key=S3_OBJECT_NAME)


def bucket_exists(bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            return False
        else:
            raise




if __name__ == "__main__":
    if not bucket_exists(S3_BUCKET_NAME):
        try:
            s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
            logger.error(f"Bucket {S3_BUCKET_NAME} created successfully.")
        except ClientError as e:
            logger.error(f"Unable to create bucket {S3_BUCKET_NAME}. Reason: {e}")
        else:
            logger.error(f"Bucket {S3_BUCKET_NAME} already exists.")

    uvicorn.run(app, host="0.0.0.0", port=8000)