from sqlalchemy import create_engine
import os

# Define the database URI with SSL required for remote connections
if 'SSL_CERTIFICATE_FILE' in os.environ:
    ssl_args = {'ssl': True, 'options': f'-K {os.environ["SSL_CERTIFICATE_FILE"]} -k {os.environ["SSL_KEY_FILE"]}'}
else:
    ssl_args = {}

# Define the database URI with SSL required for remote connections
db_uri = f'mysql+pymysql://{os.environ["MYSQL_USER"]}:{os.environ["MYSQL_PASSWORD"]}@{os.environ["MYSQL_HOST"]}:{os.environ["MYSQL_PORT"]}/database?ssl_mode=REQUIRED&{",".join(f"{k}={v}" for k,v in ssl_args.items())}'

# Create the engine with SSL required for remote connections
engine = create_engine(db_uri)
