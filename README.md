# Simple AWS Elastic Beanstalk exporter

A Prometheus Elastic Beanstalk exporter written in Python.

## Metrics

| Metrics  | Dimensions | Labels | Description |
| ------  | ------ | ------ | ----------- |
| elasticbeanstalk\_application | application_name | description | Description of Elastic Beanstalk applications |
| elasticbeanstalk\_environment_status | environment_name | id, application_name, platform, url, health, version, environment_tier | Status of Elastic Beanstalk environments |
| elasticbeanstalk\_enhanced_global_current_requests | environment_name | - | Average number of requests per second over the last 10 seconds per environment (enhanced only)|
| elasticbeanstalk\_enhanced_global_http_requests_percent | environment_name | status_code | Percent of requests that resulted in a status code over the last 10 seconds (enhanced only) |
| elasticbeanstalk\_enhanced_current_requests | environment_name, instance_id | - | Average number of requests per instance per second over the last 10 seconds (enhanced only) |
| elasticbeanstalk\_enhanced_load_average | environment_name, instance_id | mode | Load average of instances (enhanced only) |
| elasticbeanstalk\_enhanced_cpu_usage_percent | environment_name, instance_id | state | CPU Usage per instance and state (enhanced only) |
| elasticbeanstalk\_enhanced_health_status | environment_name | color, health_status | Health of environments (enhanced only) |
| elasticbeanstalk\_enhanced_status | environment_name | status | Status of environments (enhanced only) |
| elasticbeanstalk\_collector_duration_seconds | collector | - | Duration of collections |

## Configuration

Credentials to AWS are provided in the following order:

- Environment variables (AWS\_ACCESS\_KEY\_ID and AWS\_SECRET\_ACCESS\_KEY)
- Shared credentials file (~/.aws/credentials)
- IAM role for Amazon EC2

For more information see the [AWS Python SDK Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)

To gather additional metrics about resources of your environment, AWS Elastic Beanstalk Enhanced Health Reporting needs to be enabled, see the [AWS Elastic Beanstalk documentation](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/health-enhanced-enable.html)

### AWS IAM permissions

The exporter needs read access to Elastic Beanstalk service for describing applications and environments:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "elasticbeanstalk:Check*",
                "elasticbeanstalk:Describe*",
                "elasticbeanstalk:List*",
                "elasticbeanstalk:RequestEnvironmentInfo",
                "elasticbeanstalk:RetrieveEnvironmentInfo"
            ],
            "Resource": "*"
        }
    ]
}
```

## Docker Image

To run the Elastic Beanstalk exporter on Docker, you need to specify the region to connect to. Metrics are exposed on port 9552.

When running on an ec2 machine using IAM role:

```
$ docker run -e AWS_DEFAULT_REGION=<region> -d -p 9552:9552 jeremietharaud/elasticbeanstalk-exporter
```

When running it externally:

```
$ docker run -d -p 9552:9552 -e AWS_ACCESS_KEY_ID=<access_key> -e AWS_SECRET_ACCESS_KEY=<secret_key> -e AWS_DEFAULT_REGION=<region> jeremietharaud/elasticbeanstalk-exporter
```