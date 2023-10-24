#!/bin/bash
set -eo pipefail

TAG=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_REPOSITORY_APP:$CIRCLE_BUILD_NUM
DYNAMOTAG=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$AWS_REPOSITORY_DYNAMODB:$CIRCLE_BUILD_NUM

sed -i='' "s|project-tag-update:latest|$TAG|" docker-compose-local.yml
sed -i='' "s|amazon/dynamodb-local:latest|$DYNAMOTAG|" docker-compose-local.yml

docker-compose -f docker-compose-local.yml up --build

