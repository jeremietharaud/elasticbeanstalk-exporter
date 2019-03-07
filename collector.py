import boto3
from prometheus_client.core import GaugeMetricFamily


class ElasticBeanstalkCollector:
    """Class used to get metrics from an Elastic Beanstalk application.
    """

    def __init__(self):
        self.client = boto3.client('elasticbeanstalk')
        self.metric_prefix = "eb_"

    def describe_environments(self):
        environments = self.client.describe_environments()
        return environments['Environments']

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
        environments = self.describe_environments()
        applications = self.describe_applications()
        app_status = GaugeMetricFamily(self.metric_prefix + 'application_status',
                                       'Status of Elastic Beanstalk application',
                                       labels=['application_name', 'description'])
        env_status = GaugeMetricFamily(self.metric_prefix + 'environment_status',
                                       'Status of Elastic Beanstalk environment',
                                       labels=['environment_name', 'environment_id', 'application_name',
                                               'stack_name', 'alias_name'])
        for application in applications:
            app_status.add_metric([application['ApplicationName'], application['Description']], 1)
        yield app_status
        for environment in environments:
            env_status.add_metric([environment['EnvironmentName'], environment['EnvironmentId'],
                                   environment['ApplicationName'], environment['SolutionStackName'],
                                   environment['CNAME']], 1)
        yield env_status
