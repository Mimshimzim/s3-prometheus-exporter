FROM python:alpine

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT python src/main.py