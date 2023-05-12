#!/bin/bash
set -e

# there are two versions of the AWS client in our infrastructure,
# this get-login help command only works on the old version, so if it works, run the old one.
echo "ECR login"
if aws ecr get-login help &> /dev/null
then
  eval $(aws ecr get-login --region us-east-1 --no-include-email)
else
  aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 868884350453.dkr.ecr.us-east-1.amazonaws.com
fi

# The latest parameter creates two tags during deploy (tag defined in .env and latest)
# Check if the latest parameter has been set
build_file=build.yml
while (( $# >= 1 )); do
  case $1 in
    latest) build_file=build_latest.yml;;
    *) break;
  esac;
  shift
done

echo "Build docker image"
docker-compose -f $build_file build

echo "Push docker image"
docker-compose -f $build_file push