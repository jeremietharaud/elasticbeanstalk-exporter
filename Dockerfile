FROM python:alpine3.8

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir boto3 prometheus_client

CMD ["python","-u","main.py"]
