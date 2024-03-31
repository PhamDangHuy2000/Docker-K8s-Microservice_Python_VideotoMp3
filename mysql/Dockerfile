FROM mysql:8.0.34

# copy script to create DB and user
COPY ./init_db.sql /docker-entrypoint-initdb.d

EXPOSE 3306
