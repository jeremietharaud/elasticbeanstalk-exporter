from prometheus_client import start_http_server
from collector import ElasticBeanstalkCollector
import logging
import time


def main():
    logging.info("Starting http server...")
    start_http_server(9199)
    logging.info("Started http server...")
    collector = ElasticBeanstalkCollector()
    while True:
        collector.collect()
        time.sleep(10)


if __name__ == "__main__":
    main()
