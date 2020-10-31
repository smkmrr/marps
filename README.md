# marps
marps test


#docker commands
#create db image at project root
sudo docker build . -t marps_db:1.0.0

#run db
sudo docker run -p 5432:5432 marps_db:1.0.0

sudo docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d marps_db:1.0.0

