FROM postgres
WORKDIR /docker-entrypoint-initdb.d
ADD /db/schema.sql /docker-entrypoint-initdb.d
EXPOSE 5432