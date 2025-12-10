-- Store password as an environment variable or a secure config file
SET @password = 'mypassword';

CREATE DATABASE myapplication;

-- Create a new user for the application with hashed password
CREATE USER 'myappuser'@'192.168.1.%' IDENTIFIED BY PASSWORD (PASSWORD(@password));

-- Create roles for specific actions to maintain data integrity
CREATE ROLE 'myapp_read_only';
CREATE ROLE 'myapp_insert_update';

-- Grant necessary privileges to the new user
GRANT SELECT ON myapplication.* TO 'myappuser'@'192.168.1.%';
GRANT INSERT, UPDATE ON myapplication.* TO 'myappuser'@'192.168.1.%';

-- Assign roles for specific actions
SET ROLE 'myapp_read_only' FOR USER 'myappuser'@'192.168.1.%';
SET ROLE 'myapp_insert_update' FOR USER 'myappuser'@'192.168.1.%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;
