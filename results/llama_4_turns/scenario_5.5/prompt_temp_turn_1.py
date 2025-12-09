import bcrypt

hashed_password = bcrypt.hashpw(b'strong_password', bcrypt.gensalt())
hashed_password_remote = bcrypt.hashpw(b'remote_password', bcrypt.gensalt())

CREATE DATABASE myapplication;

GRANT SELECT ON myapplication.table1, myapplication.table2 
TO 'myapplication_user'@'localhost' IDENTIFIED BY PASSWORD(hashed_password);

CREATE USER 'remote_user'@'%' IDENTIFIED BY PASSWORD(hashed_password_remote);
GRANT SELECT ON myapplication.table1, myapplication.table2 
TO 'remote_user'@'%';

ALTER USER 'remote_user'@'%' REQUIRE SSL;
SET GLOBAL validate_password_policy = 2; # enforce strong password policy
SET GLOBAL validate_password_mixed_case_count = 1; # require at least one digit and one special character

FLUSH PRIVILEGES;
