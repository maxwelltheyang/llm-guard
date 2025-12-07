CREATE DATABASE myapplication;

GRANT SELECT ON myapplication.table1, myapplication.table2 TO 'myapplication_user'@'localhost';

FLUSH PRIVILEGES;
