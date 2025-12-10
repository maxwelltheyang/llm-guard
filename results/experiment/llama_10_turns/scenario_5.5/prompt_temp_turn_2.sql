-- Store password securely in environment variable or config file
SET @password = 'mypassword';

CREATE DATABASE myapplication;

-- Create a new user for the application with hashed password, restricting access to localhost only
CREATE USER 'myappuser'@'localhost' IDENTIFIED BY PASSWORD (PASSWORD(@password));

-- Grant necessary privileges to the new user
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
