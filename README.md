# marps
marps test


#docker commands
#create db image at project root
sudo docker build . -t marps_db:1.0.0
docker rm $(docker ps -a -q)
#run db
sudo docker run --name marps_db -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d marps_db:1.0.0


#OR
. prepare_run_db.sh

