CREATE DATABASE myapp;

CREATE USER 'myappuser'@'%' IDENTIFIED BY 'mypassword';

GRANT ALL PRIVILEGES ON myapp.* TO 'myappuser'@'%';

FLUSH PRIVILEGES;
