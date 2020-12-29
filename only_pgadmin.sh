#!/bin/sh
docker stop pgadmin

docker rm -f pgadmin

docker run -p 5050:5050 --name pgadmin --network=pg -e "PGADMIN_DEFAULT_EMAIL=myemail@gmail.com" -e "PGADMIN_DEFAULT_PASSWORD=a12345678" -v /home/pi/PycharmProjects/marps/servers.json:/pgadmin4/servers.json -d biarms/pgadmin4

