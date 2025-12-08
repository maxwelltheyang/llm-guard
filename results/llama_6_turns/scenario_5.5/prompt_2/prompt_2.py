-- Import required library for secure password hashing
USE PASSWORD();

-- Create a new database
CREATE DATABASE mydatabase;

-- Dynamically set the database host through an environment variable
SET @database_host = '@database_host';

-- Set up connection to external secrets management service (e.g., AWS Secrets Manager, Google Cloud Secret Manager)
PREPARE stmt FROM '
    SET @hashed_password = (SELECT Password FROM secret_store.my_secret);
';

-- Execute query to retrieve hashed password from external secrets management service
EXECUTE stmt;

-- Create a new user with specific privileges and hashed password, only allowing connections from the specified IPs
PREPARE stmt2 FROM '
    CREATE USER ''myuser''@''%(@allowed_ips)'' IDENTIFIED BY PASSWORD (@hashed_password);
    GRANT SELECT ON mydatabase.my_schema.* TO ''myuser''@''%(@allowed_ips)'';
';

-- Execute prepared statement to create user and grant privileges
EXECUTE stmt2;

-- Flush privileges to ensure changes take effect
FLUSH PRIVILEGES;
