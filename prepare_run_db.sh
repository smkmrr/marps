#!/bin/sh

sudo docker build . -t marps_db:1.0.0
docker rm -f $(docker ps -a -q)
sudo docker run --name marps_db -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d marps_db:1.0.0