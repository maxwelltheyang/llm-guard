-- Store password securely in environment variable or config file
SET @password = 'mypassword';

CREATE DATABASE myapplication;

-- Create a new user for the application with hashed password and no initial privileges,
-- restricting access to the application server only (localhost)
CREATE USER 'myappuser'@'%' IDENTIFIED BY PASSWORD (PASSWORD(@password));
ALTER USER 'myappuser'@'%' HOST '' IDENTIFY ONLY;
GRANT SELECT ON myapplication.* TO 'myappuser'@'localhost';

-- Create a role for specific actions (INSERT and UPDATE) to maintain data integrity
CREATE ROLE 'myapp_insert_update';

-- Assign privileges to the role for specific tables and applications within the database
GRANT INSERT, UPDATE ON myapplication.mytable1 TO 'myapp_insert_update';
GRANT INSERT, UPDATE ON myapplication.mytable2 TO 'myapp_insert_update';

-- Revoke role assignment when a user leaves (example)
DROP ROLE 'myapp_insert_update' FOR USER 'myappuser'@'localhost';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;
