CREATE TABLE villager (
	id serial PRIMARY KEY,
	name VARCHAR ( 50 ) UNIQUE,
	rfId NUMERIC ( 10 ) NOT NULL,
	email VARCHAR ( 255 ) UNIQUE,
	created_on TIMESTAMP NOT NULL
);