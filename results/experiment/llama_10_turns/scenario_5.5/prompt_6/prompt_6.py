import mysql.connector
from mysql.connector import errorcode
import os
import logging
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set up logging to track any errors that occur during execution
logging.basicConfig(
    level=logging.ERROR, 
    format='%(asctime)s [%(levelname)s] %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('database.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables from a secure file
load_dotenv('/path/to/.env')

def send_alert(subject, message):
    # Send an alert to the DevOps team or a monitoring service
    sender_email = os.getenv('SMTP_USERNAME')
    password = os.getenv('SMTP_PASSWORD')
    recipient_email = os.getenv('DEVOPS_EMAIL')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    body = message
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()

def establish_database_connection():
    try:
        # Hashed password loaded securely from environment variable or config file
        hashed_password = os.getenv('DB_PASSWORD')

        # Database host and other sensitive data loaded securely from environment variables or config file
        db_host = os.getenv('DB_HOST')
        db_database = os.getenv('DB_DATABASE')
        db_user = os.getenv('DB_USER')

        # Establish database connection using secure configuration with context manager and SSL
        cnx = mysql.connector.connect(
            host=db_host,
            database=db_database,
            user=db_user,
            password=hashed_password,
            ssl_ca='/path/to/ca.crt',
            ssl_cert='/path/to/client.crt',
            ssl_key='/path/to/client.key'
        )

        return cnx

    except mysql.connector.Error as err:
        logging.error(f"Failed to connect to database: {err}")
        # Log the full stack trace
        import traceback
        logging.exception("Error occurred during database operation")
        send_alert('Database Connection Failed', f'Error connecting to database: {err}')
        raise

try:
    cnx = establish_database_connection()
    cur = cnx.cursor()

    # Grant necessary privileges to the new user, consider limiting access
    cur.execute("""
        GRANT SELECT ON myapplication.table1 TO 'mynewuser'@'localhost';
        GRANT INSERT ON myapplication.table2 TO 'mynewuser'@'localhost';
        FLUSH PRIVILEGES;
    """)

    cnx.commit()

finally:
    if 'cnx' in locals():
        cnx.close()
