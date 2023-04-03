#!/bin/bash -eux
docker-compose up --build --remove-orphans -d
docker-compose ps