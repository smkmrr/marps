CREATE DATABASE marps_db
   WITH
   OWNER postgres
   TEMPLATE template0
   ENCODING 'UTF-8'
   TABLESPACE  pg_default
   LC_COLLATE  'C'
   LC_CTYPE  'C'
   CONNECTION LIMIT  -1;

CREATE TABLE company (
	id integer PRIMARY KEY,
	name VARCHAR ( 50 ) UNIQUE,
	code NUMERIC ( 10 ) NOT NULL,
	email VARCHAR ( 255 ) UNIQUE,
	created_on TIMESTAMP NOT NULL
);
CREATE TABLE villager (
	id integer PRIMARY KEY,
	name VARCHAR ( 50 ) UNIQUE,
	rfId VARCHAR ( 10 ) NOT NULL,
	companyId integer not null references company(id),
	created_on TIMESTAMP NOT NULL
);



INSERT INTO company(id, name, code, email, created_on) VALUES ( 102, 'Meganova', 1002, 'info@meganova.se', NOW());
INSERT INTO company(id, name, code, email, created_on) VALUES ( 101, 'A Village', 1001, 'info@avillage.se', NOW());
INSERT INTO villager(id, name, rfId, companyId, created_on) VALUES (123, 'Ali Akyel', '0000792099', 102, NOW());
INSERT INTO villager(id, name, rfId, companyId, created_on) VALUES (124, 'Deniz Ozen', '0005713678', 102, NOW());
INSERT INTO villager(id, name, rfId, companyId, created_on) VALUES (127, 'Mesut Yilmaz', '0005728272', 101, NOW());
