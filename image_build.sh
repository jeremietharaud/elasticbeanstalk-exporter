#!/bin/bash
set -e

echo "Build docker image"
docker-compose -f build.yml build