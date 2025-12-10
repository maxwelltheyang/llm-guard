-- Store password as an environment variable or a secure config file
SET @password = 'mypassword';

CREATE DATABASE myapplication;

-- Create a new user for the application with hashed password and no initial privileges
CREATE USER 'myappuser'@'192.168.1.%' IDENTIFIED BY PASSWORD (PASSWORD(@password));

-- Grant necessary privileges to the new user, initially only SELECT on all tables
GRANT SELECT ON myapplication.* TO 'myappuser'@'192.168.1.%';

-- Create a role for specific actions (INSERT and UPDATE) to maintain data integrity
CREATE ROLE 'myapp_insert_update';

-- Assign privileges to the role for specific tables and applications within the database
GRANT INSERT, UPDATE ON myapplication.mytable1 TO 'myapp_insert_update';
GRANT INSERT, UPDATE ON myapplication.mytable2 TO 'myapp_insert_update';

-- Create a view to encapsulate queries that require these actions (INSERT and UPDATE)
CREATE VIEW v_myview AS SELECT * FROM myapplication.mytable1;

-- Assign the role to the user only when necessary
SET ROLE 'myapp_insert_update' FOR USER 'myappuser'@'192.168.1.%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;
