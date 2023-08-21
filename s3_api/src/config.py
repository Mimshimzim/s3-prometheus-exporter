
# S3 Configuration
from botocore.client import Config
import os

S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_OBJECT_NAME = "obj1"
S3_CONFIG = Config(connect_timeout=10,  retries = {'max_attempts': 1,'mode': 'standard'})
S3_BUCKET_LIFECYCLE_CONFIGURATION = {
            "Rules": [
                {
                    "ID": "MoveToGlacierAndDelete",
                    "Prefix": "",
                    "Status": "Enabled",
                    "Expiration": {
                        "Days": 365
                    }
                }
            ]
            }
S3_BUCKET_CORS_CONFIGURATION = {
          'CORSRules': [{
               'AllowedHeaders': ['Authorization'],
               'AllowedMethods': ['GET','PUT','HEAD','POST'],
               'AllowedOrigins': ['*'],
               'ExposeHeaders': ['GET','PUT','POST'],
               'MaxAgeSeconds': 3000
           }]
        }
S3_OBJECT_TAGGING_CONFIGURATION = {
            'TagSet': [
                {
                'Key': 's3-provider',
                'Value': 'arvanstorage'
                },
                ]
            }

