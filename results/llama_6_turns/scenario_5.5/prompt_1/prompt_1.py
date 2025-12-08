-- Import required library for secure password hashing
USE PASSWORD();
SET @hashed_password = SHA2('mysecretpassword', 256);

-- Create a new database
CREATE DATABASE mydatabase;

-- Inject the hashed password securely through an environment variable (more details in external secrets management service)
SET @password = '@hashed_password';

-- Create a new user with specific privileges and hashed password
CREATE USER 'myuser'@'localhost' IDENTIFIED BY PASSWORD(@password);

-- Grant SELECT privilege on the database's specific schema (for example, 'my_schema')
GRANT SELECT ON mydatabase.my_schema.* TO 'myuser'@'localhost';

-- Flush privileges to ensure changes take effect
FLUSH PRIVILEGES;
