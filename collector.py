import boto3
from prometheus_client.core import GaugeMetricFamily
import logging


class Logger:
    """Class used to display logs on the console.
    """

    def __init__(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        self.logger = logger


class ElasticBeanstalkCollector:
    """Class used to get metrics from an Elastic Beanstalk application.
    """

    def __init__(self):
        self.client = boto3.client('elasticbeanstalk')
        self.metric_prefix = "elasticbeanstalk_"
        self.logger = Logger().logger

    def describe_environments(self):
        environments = self.client.describe_environments()
        return environments['Environments']

    def list_environment_tags(self, environment_arn):
        tags = self.client.list_tags_for_resource(
               ResourceArn=environment_arn
        )
        return tags['ResourceTags']

    def describe_applications(self):
        applications = self.client.describe_applications()
        return applications['Applications']

    def describe_environment_health(self, environment):
        metrics = None
        try:
            metrics = self.client.describe_environment_health(
                EnvironmentName=environment,
                AttributeNames=['All']
            )
        except Exception as err:
            print(err)
        return metrics

    def collect(self):
        self.logger.info("Collect metrics")
        environments = self.describe_environments()
        applications = self.describe_applications()
        app = GaugeMetricFamily(
            self.metric_prefix + 'application',
            'Description of Elastic Beanstalk application',
            labels=['application_name', 'description']
        )
        env = GaugeMetricFamily(
            self.metric_prefix + 'environment_status',
            'Status of Elastic Beanstalk environment',
            labels=['environment_name', 'id', 'application_name',
                    'platform', 'url', 'health', 'version', 'environment_tier']
        )
        for application in applications:
            app.add_metric(
                [application['ApplicationName'], self.get_label_value(application, 'Description')], 1
            )
        yield app
        for environment in environments:
            env.add_metric(
                [environment['EnvironmentName'], environment['EnvironmentId'],
                 environment['ApplicationName'], environment['PlatformArn'],
                 environment['CNAME'], environment['Health'],
                 self.get_label_value(environment, 'VersionLabel'),
                 environment['Tier']['Name']],
                1 if environment['Health'] == 'Green' else 0
            )
        yield env

    @staticmethod
    def get_label_value(obj, label):
        if label in obj:
            return obj[label]
        else:
            return ''
