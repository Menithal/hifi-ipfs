#!/bin/bash
docker-compose stop gatekeeper;
docker-compose rm -f gatekeeper;
docker-compose pull gatekeeper;
docker-compose build gatekeeper;

docker-compose up -d gatekeeper;