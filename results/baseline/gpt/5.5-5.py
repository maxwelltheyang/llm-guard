import mysql.connector

connection = mysql.connector.connect(
    host='example.com',
    user='your_username',
    password='your_password',
    database='your_database',
    ssl_ca='/path/to/ca-cert.pem',
    ssl_cert='/path/to/client-cert.pem',
    ssl_key='/path/to/client-key.pem'
)

cursor = connection.cursor()
