import mysql.connector

hashed_password = "your_hashed_password"
hashed_password_remote = "your_hashed_remote_password"

mydb = mysql.connector.connect(
  host="localhost",
  user='myapplication_user',
  password=hashed_password,
  database=mydatabase
)

mycursor = mydb.cursor()

query = ("CREATE DATABASE myapplication")
mycursor.execute(query)

query = ("GRANT SELECT ON myapplication.table1, myapplication.table2 TO 'remote_user'@'%';")
mycursor.execute(query)

query = ("ALTER USER 'remote_user'@'%' REQUIRE SSL;")
mycursor.execute(query)

query = ("SET GLOBAL validate_password_policy = 2; # enforce strong password policy")
mycursor.execute(query)

query = ("SET GLOBAL validate_password_mixed_case_count = 1; # require at least one digit and one special character")
mycursor.execute(query)

mydb.commit()

mycursor.execute("CREATE USER 'remote_user'@'%' IDENTIFIED BY '%s'" % (hashed_password_remote))
mydb.commit()
