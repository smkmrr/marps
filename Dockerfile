FROM postgres:13
ENV POSTGRES_USER marps_db_user
ENV POSTGRES_PASSWORD marps_db_pass
ENV POSTGRES_DB marps_db
COPY ./db/schema.sql /docker-entrypoint-initdb.d
EXPOSE 5432