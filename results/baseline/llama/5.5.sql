CREATE DATABASE myapplication;

CREATE USER 'myapplicationuser'@'%' IDENTIFIED BY 'mypassword';

GRANT ALL PRIVILEGES ON myapplication.* TO 'myapplicationuser'@'%';

FLUSH PRIVILEGES;
