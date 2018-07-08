#!/usr/local/bin/powershell


# Use PS only for dev, this one is only used for developing as the volumes do not persist.
# TODO: investigate persistance issues with the config


docker-compose -f dev-compose.yml stop;
docker-compose -f dev-compose.yml rm -f;
docker-compose -f dev-compose.yml pull;
docker-compose -f dev-compose.yml build;

docker-compose -f dev-compose.yml up -d --force-recreate;