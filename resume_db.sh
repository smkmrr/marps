#!/bin/sh
docker rm -f marps_db
docker build -f DockerfileResume . -t marps_db_empty:1.0.0
docker run --name marps_db --network=pg -p 5432:5432 -v marps_db:/var/lib/postgresql/data -d marps_db_empty:1.0.0

