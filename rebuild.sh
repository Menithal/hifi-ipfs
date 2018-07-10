#!/bin/bash
docker-compose stop upload-point;
docker-compose rm -f upload-point;
docker-compose pull upload-point;
docker-compose build upload-point;

docker-compose up -d upload-point;