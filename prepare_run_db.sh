#!/bin/sh
docker stop marps_db
docker rm -f marps_db
docker network create pg
docker build . -t marps_db:1.0.0
docker run --name marps_db --network=pg -p 5432:5432 -v marps_db:/var/lib/postgresql/data -d marps_db:1.0.0

