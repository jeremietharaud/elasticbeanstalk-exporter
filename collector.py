import boto3
from prometheus_client import Gauge


class ElasticBeanstalkCollector:
    """Class used to get metrics from an Elastic Beanstalk application.
    """

    def __init__(self):
        self.client = boto3.client('elasticbeanstalk')
        self.environment_gauge = Gauge('elasticbeanstalk_environment_total', 'Number of environments')
        self.application_gauge = Gauge('elasticbeanstalk_application_total', 'Number of applications')

    def describe_environments(self):
        environments = []
        environments_list = self.client.describe_environments()
        for environment in environments_list['Environments']:
            environments.append(environment['EnvironmentName'])
        return environments

    def describe_applications(self):
        applications = []
        applications_list = self.client.describe_applications()
        for application in applications_list['Applications']:
            applications.append(application['ApplicationName'])
        return applications

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
        self.describe_environments()
        self.describe_applications()
