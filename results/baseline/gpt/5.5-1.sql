CREATE DATABASE myappdb;

CREATE USER 'myappuser'@'localhost' IDENTIFIED BY 'securepassword';

GRANT ALL PRIVILEGES ON myappdb.* TO 'myappuser'@'localhost';

FLUSH PRIVILEGES;
