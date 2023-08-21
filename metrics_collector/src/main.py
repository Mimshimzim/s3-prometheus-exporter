from fastapi import FastAPI, Depends
from prometheus_client import Histogram, generate_latest
import uvicorn
import httpx
import logging
from fastapi.responses import PlainTextResponse
import os

# Setup logging
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

app = FastAPI()

# Prometheus histogram definition
PRODUCT_LATENCY = Histogram(
    "arvan_s3_latency", "Latency for S3 Endpoints", ["api", 'endpoint','source'],
    buckets=["0.5", "2", "5", "10"]
)

ROUTES = [
    "put-s3-object",
    "put-s3-bucket-acl-public",
    "put-s3-bucket-acl-private",
    "put-s3-object-tagging",
    "list-s3-buckets",
    "list-s3-objects",
    "get-s3-bucket-acl",
    "get-s3-object",
    "get-s3-object-tagging",
    "delete-s3-object-tagging",
    "delete-s3-object"
]


# Dependency to get the async http client
async def get_http_client():
    return httpx.AsyncClient()


@app.get("/metrics",response_class=PlainTextResponse)
async def collect_s3_metrics(client: httpx.AsyncClient = Depends(get_http_client)):
    results = {}

    for route in ROUTES:
        try:
            response = await client.get(f'http://s3_api_metrics:8000/{route}')
            #response.raise_for_status()

            data = response.json()
            api = data.get("api")
            endpoint = data.get("endpoint")
            latency = float(data.get("latency", 0))
            source=os.getenv("SOURCE")
            PRODUCT_LATENCY.labels(api, endpoint,source).observe(latency)

        except (httpx.RequestError, ValueError) as e:
            logger.error(f"Error occurred while fetching metrics for route {route}: {str(e)}")
            results[route] = {"latency": "N/A", "api": "N/A", "endpoint": "N/A"}

    await client.aclose()
    return generate_latest()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
