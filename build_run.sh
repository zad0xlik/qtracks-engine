#!/bin/bash

#AWS_DEFAULT_REGION="US-WEST-2"
#AWS_SESSION_TOKEN="TOKEN"
#AWS_SECRET_ACCESS_KEY="KEY"
#AWS_ACCESS_KEY_ID="KEY_ID"
#PGPASSWORD="Rivka2019"
#PROJECT_NAME="nsight-mtg-management"
#USER_EMAIL="fedor.kolyadin@nomissolutions.com"
#USER_NAME="Fedor Kolyadin"
#GIT_HOST="zeus.nomissolutions.com"


docker build -t "qtrack-backend" -f Dockerfile .

#docker build -t "qtrack-backend" -f Dockerfile \
#          --build-arg PROJECT_NAME=qtrack-backend \
#          --build-arg PYTHON_VERSION_TAG=3.7.3 \
#          --build-arg LINK_PYTHON_TO_PYTHON3=1 .

#ports to be exposed
#EXPOSE 5000
#EXPOSE 5432
#EXPOSE 6060
#EXPOSE 6379

docker run -p 80:5000 \
          -p 5432:5432 \
          -p 6060:6060 \
          -p 6379:6379 \
          qtrack-backend:latest
