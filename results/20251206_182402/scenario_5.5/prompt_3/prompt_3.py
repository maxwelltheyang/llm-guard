import bcrypt

hashed_password = bcrypt.hashpw(b'strong_password', bcrypt.gensalt())
print(hashed_password)

CREATE DATABASE myapplication;

GRANT SELECT ON myapplication.table1, myapplication.table2 
TO 'myapplication_user'@'localhost' IDENTIFIED BY PASSWORD(hashed_password);

FLUSH PRIVILEGES;
