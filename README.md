# Simple AWS Elastic Beanstalk exporter

A Prometheus Elastic Beanstalk exporter

## Metrics

TODO

## Configuration

Credentials to AWS are provided in the following order:

- Environment variables (AWS\_ACCESS\_KEY\_ID and AWS\_SECRET\_ACCESS\_KEY)
- Shared credentials file (~/.aws/credentials)
- IAM role for Amazon EC2

For more information see the [AWS Python SDK Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)

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

## Running

**You need to specify the region you to connect to**
Running on an ec2 machine using IAM roles:
`docker run -e AWS_REGION=<region> -d -p 9199:9199 jeremietharaud/elasticbeanstalk-exporter`

Or running it externally:
`docker run -d -p 9199:9199 -e AWS_ACCESS_KEY_ID=<access_key> -e AWS_SECRET_ACCESS_KEY=<secret_key> -e AWS_REGION=<region>  jeremietharaud/elasticbeanstalk-exporter`