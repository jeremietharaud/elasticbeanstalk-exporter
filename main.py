from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from collector import ElasticBeanstalkCollector
import logging
import time
import datetime


def main():
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], "Starting exporter on :9552")
    start_http_server(9552)
    collector = ElasticBeanstalkCollector()
    REGISTRY.register(collector)
    while True:
        collector.collect()
        time.sleep(60)


if __name__ == "__main__":
    main()
