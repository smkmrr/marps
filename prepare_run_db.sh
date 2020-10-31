#!/bin/sh

sudo docker build . -t marps_db:1.0.0
sudo docker rm -f $(docker ps -a -q)
sudo docker run --name marps_db -e POSTGRES_PASSWORD=12 -e POSTGRES_USER=postgres -e POSTGRES_DB=marps_db  -p 5432:5432  marps_db:1.0.0
