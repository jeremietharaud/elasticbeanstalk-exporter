FROM python:alpine3.8

WORKDIR /elasticbeanstalk-exporter

RUN pip install --no-cache-dir boto3 prometheus_client

COPY . .

EXPOSE 9552

CMD ["python","-u","main.py"]
