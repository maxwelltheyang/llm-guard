CREATE DATABASE myapplication;

GRANT SELECT ON myapplication.table1, myapplication.table2 
TO 'myapplication_user'@'localhost' IDENTIFIED BY PASSWORD('strong_password');

FLUSH PRIVILEGES;
