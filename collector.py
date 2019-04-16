import boto3
import botocore
from prometheus_client.core import GaugeMetricFamily
import logging
import time
from joblib import Parallel, delayed


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
        self.metric_collector_duration = None

    def describe_environments(self):
        environments = self.client.describe_environments(IncludeDeleted=False)
        return environments['Environments']

    def describe_applications(self):
        applications = self.client.describe_applications()
        return applications['Applications']

    def parallel_describe_environment_health(self, environment):
        metrics = None
        try:
            metrics = self.client.describe_environment_health(
                EnvironmentName=environment,
                AttributeNames=['All']
            )
        except botocore.exceptions.ClientError as e:
            if e.response.get("Error").get("Code") == "InvalidRequestException":
                return "None", "None"
            else:
                raise e
        return environment, metrics

    def parallel_describe_environment_instances_health(self, environment):
        metrics = None
        try:
            metrics = self.client.describe_instances_health(
                EnvironmentName=environment,
                AttributeNames=['HealthStatus', 'ApplicationMetrics', 'System']
            )
        except botocore.exceptions.ClientError as e:
            if e.response.get("Error").get("Code") == "InvalidRequestException":
                return "None", "None"
            else:
                raise e
        return environment, metrics['InstanceHealthList']

    def collect_applications(self, applications):
        start = time.time()
        app = GaugeMetricFamily(
            self.metric_prefix + 'application',
            'Description of Elastic Beanstalk application',
            labels=['application_name', 'description']
        )
        for application in applications:
            app.add_metric(
                [application['ApplicationName'],
                 self.get_label_value(application, 'Description')], 1
            )
        end = time.time()
        self.metric_collector_duration.add_metric(['applications'], end-start)
        return app

    def collect_environments(self, environments):
        start = time.time()
        env = GaugeMetricFamily(
            self.metric_prefix + 'environment_status',
            'Status of Elastic Beanstalk environment',
            labels=['environment_name', 'id', 'application_name',
                    'platform', 'url', 'health', 'version', 'environment_tier']
        )
        for environment in environments:
            env.add_metric(
                [environment['EnvironmentName'], environment['EnvironmentId'],
                 environment['ApplicationName'], environment['PlatformArn'],
                 self.get_label_value(environment, 'CNAME'), environment['Health'],
                 self.get_label_value(environment, 'VersionLabel'),
                 environment['Tier']['Name']],
                1 if environment['Health'] == 'Green' else 0
            )
        end = time.time()
        self.metric_collector_duration.add_metric(['environments'], end-start)
        return env

    def collect_global_current_requests(self, environments_health):
        start = time.time()
        current_requests = GaugeMetricFamily(
            self.metric_prefix + 'environment_enhanced_global_current_requests',
            'Average number of requests per second over the last 10 seconds',
            labels=['environment_name']
        )
        for environment, health in environments_health:
            if health != "None" and 'ApplicationMetrics' in health:
                current_requests.add_metric(
                    [environment], health['ApplicationMetrics']['RequestCount']
                )
        end = time.time()
        self.metric_collector_duration.add_metric(['global_current_requests'], end-start)
        return current_requests

    def collect_current_requests(self, environments_instances_health):
        start = time.time()
        instance_current_requests = GaugeMetricFamily(
            self.metric_prefix + 'environment_enhanced_current_requests',
            'Average number of requests per instance per second over the last 10 seconds',
            labels=['environment_name', 'instance_id']
        )
        for environment, instances_health in environments_instances_health:
            if instances_health != "None":
                for instance_health in instances_health:
                    instance_current_requests.add_metric(
                        [environment, instance_health['InstanceId']],
                        instance_health['ApplicationMetrics']['RequestCount']
                    )
        end = time.time()
        self.metric_collector_duration.add_metric(['current_requests'], end-start)
        return instance_current_requests

    def collect_load_average(self, environments_instances_health):
        start = time.time()
        instance_load_average = GaugeMetricFamily(
            self.metric_prefix + 'environment_enhanced_load_average',
            'Load average in the last 1-minute, 5-minute, and 15-minute periods',
            labels=['environment_name', 'instance_id', 'mode']
        )
        for environment, instances_health in environments_instances_health:
            if instances_health != "None":
                for instance_health in instances_health:
                    instance_load_average.add_metric(
                        [environment,
                         instance_health['InstanceId'], 'Load1'],
                        instance_health['System']['LoadAverage'][0]
                    )
                    instance_load_average.add_metric(
                        [environment,
                         instance_health['InstanceId'], 'Load5'],
                        instance_health['System']['LoadAverage'][1]
                    )
                    instance_load_average.add_metric(
                        [environment,
                         instance_health['InstanceId'], 'Load15'],
                        instance_health['System']['LoadAverage'][2]
                    )
        end = time.time()
        self.metric_collector_duration.add_metric(['load_average'], end-start)
        return instance_load_average

    def collect_cpu_usage(self, environments_instances_health):
        start = time.time()
        instance_cpu_usage = GaugeMetricFamily(
            self.metric_prefix + 'environment_enhanced_cpu_usage_percent',
            'CPU utilization per instance and state',
            labels=['environment_name', 'instance_id', 'state']
        )
        for environment, instances_health in environments_instances_health:
            if instances_health != "None":
                for instance_health in instances_health:
                    instance_cpu_usage.add_metric(
                        [environment,
                         instance_health['InstanceId'], 'User'],
                        instance_health['System']['CPUUtilization']['User']
                    )
                    instance_cpu_usage.add_metric(
                        [environment,
                         instance_health['InstanceId'], 'Nice'],
                        instance_health['System']['CPUUtilization']['Nice']
                    )
                    instance_cpu_usage.add_metric(
                        [environment,
                         instance_health['InstanceId'], 'System'],
                        instance_health['System']['CPUUtilization']['System']
                    )
                    instance_cpu_usage.add_metric(
                        [environment,
                         instance_health['InstanceId'], 'Idle'],
                        instance_health['System']['CPUUtilization']['Idle']
                    )
                    instance_cpu_usage.add_metric(
                        [environment,
                         instance_health['InstanceId'], 'IOWait'],
                        instance_health['System']['CPUUtilization']['IOWait']
                    )
                    instance_cpu_usage.add_metric(
                        [environment,
                         instance_health['InstanceId'], 'IRQ'],
                        instance_health['System']['CPUUtilization']['IRQ']
                    )
                    instance_cpu_usage.add_metric(
                        [environment,
                         instance_health['InstanceId'], 'SoftIRQ'],
                        instance_health['System']['CPUUtilization']['SoftIRQ']
                    )
        end = time.time()
        self.metric_collector_duration.add_metric(['cpu_usage'], end-start)
        return instance_cpu_usage

    def collect_global_http_requests(self, environments_health):
        start = time.time()
        http_requests = GaugeMetricFamily(
            self.metric_prefix + 'environment_enhanced_global_http_requests_percent',
            'Percent of requests that resulted in a status code over the last 10 seconds',
            labels=['environment_name', 'status_code']
        )
        for environment, health in environments_health:
            if health != "None" and 'ApplicationMetrics' in health:
                http_requests.add_metric(
                    [environment, 'Status2xx'],
                    health['ApplicationMetrics']['StatusCodes']['Status2xx'] if 'StatusCodes' in health['ApplicationMetrics'] else 0
                )
                http_requests.add_metric(
                    [environment, 'Status3xx'],
                    health['ApplicationMetrics']['StatusCodes']['Status3xx'] if 'StatusCodes' in health['ApplicationMetrics'] else 0
                )
                http_requests.add_metric(
                    [environment, 'Status4xx'],
                    health['ApplicationMetrics']['StatusCodes']['Status4xx'] if 'StatusCodes' in health['ApplicationMetrics'] else 0
                )
                http_requests.add_metric(
                    [environment, 'Status5xx'],
                    health['ApplicationMetrics']['StatusCodes']['Status5xx'] if 'StatusCodes' in health['ApplicationMetrics'] else 0
                )
        end = time.time()
        self.metric_collector_duration.add_metric(['global_http_requests'], end-start)
        return http_requests

    def collect_health_status(self, environments_health):
        start = time.time()
        health_status = GaugeMetricFamily(
            self.metric_prefix + 'environment_enhanced_health_status',
            'The health status of the environment',
            labels=['environment_name', 'color', 'health_status']
        )
        for environment, health in environments_health:
            if health != "None" and 'ApplicationMetrics' in health:
                health_status.add_metric(
                    [environment, 'Green', 'Ok'],
                    1 if health['HealthStatus'] == 'Ok' else 0
                )
                health_status.add_metric(
                    [environment, 'Yellow', 'Warning'],
                    1 if health['HealthStatus'] == 'Warning' else 0
                )
                health_status.add_metric(
                    [environment, 'Red', 'Degraded'],
                    1 if health['HealthStatus'] == 'Degraded' else 0
                )
                health_status.add_metric(
                    [environment, 'Red', 'Severe'],
                    1 if health['HealthStatus'] == 'Severe' else 0
                )
                health_status.add_metric(
                    [environment, 'Green', 'Info'],
                    1 if health['HealthStatus'] == 'Info' else 0
                )
                health_status.add_metric(
                    [environment, 'Grey', 'Pending'],
                    1 if health['HealthStatus'] == 'Pending' else 0
                )
                health_status.add_metric(
                    [environment, 'Grey', 'Unknown'],
                    1 if health['HealthStatus'] == 'Unknown' else 0
                )
                health_status.add_metric(
                    [environment, 'Grey', 'Suspended'],
                    1 if health['HealthStatus'] == 'Suspended' else 0
                )
        end = time.time()
        self.metric_collector_duration.add_metric(['health_status'], end-start)
        return health_status

    def collect_status(self, environments_health):
        start = time.time()
        status = GaugeMetricFamily(
            self.metric_prefix + 'environment_enhanced_status',
            'The status of the environment',
            labels=['environment_name', 'status']
        )
        for environment, health in environments_health:
            if health != "None" and 'ApplicationMetrics' in health:
                status.add_metric(
                    [environment, 'Ready'],
                    1 if health['Status'] == 'Ready' else 0
                )
                status.add_metric(
                    [environment, 'Launching'],
                    1 if health['Status'] == 'Launching' else 0
                )
                status.add_metric(
                    [environment, 'Updating'],
                    1 if health['Status'] == 'Updating' else 0
                )
                status.add_metric(
                    [environment, 'Terminating'],
                    1 if health['Status'] == 'Terminating' else 0
                )
                status.add_metric(
                    [environment, 'Terminated'],
                    1 if health['Status'] == 'Terminated' else 0
                )
        end = time.time()
        self.metric_collector_duration.add_metric(['status'], end-start)
        return status

    def collect(self):
        self.logger.info("Collect metrics")
        self.metric_collector_duration = GaugeMetricFamily(
            self.metric_prefix + 'collector_duration_seconds',
            'Duration of a collection', labels=['collector'])
        environments = self.describe_environments()
        applications = self.describe_applications()
        environments_health = Parallel(n_jobs=-1, prefer="threads")(delayed(self.parallel_describe_environment_health)(environment['EnvironmentName']) for environment in environments)
        environments_instances_health = Parallel(n_jobs=-1, prefer="threads")(delayed(self.parallel_describe_environment_instances_health)(environment['EnvironmentName']) for environment in environments)

        yield self.collect_environments(environments)
        yield self.collect_applications(applications)
        yield self.collect_global_current_requests(environments_health)
        yield self.collect_global_http_requests(environments_health)
        yield self.collect_health_status(environments_health)
        yield self.collect_status(environments_health)
        yield self.collect_current_requests(environments_instances_health)
        yield self.collect_load_average(environments_instances_health)
        yield self.collect_cpu_usage(environments_instances_health)
        yield self.metric_collector_duration

    @staticmethod
    def get_label_value(obj, label):
        if label in obj:
            return obj[label]
        else:
            return ''
