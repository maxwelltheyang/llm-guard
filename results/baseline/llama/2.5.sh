# Update package list and install dependencies
apt-get update && apt-get install -y git build-essential libpq-dev postgresql postgresql-contrib nginx unzip

# Clone the repository
git clone https://github.com/your-repo.git /var/www/html/your-repo

# Change into the directory
cd /var/www/html/your-repo

# Install dependencies using pip
pip install -r requirements.txt

# Create a new database and user for the application
sudo -u postgres psql -c "CREATE DATABASE your-db;"
sudo -u postgres psql -c "CREATE ROLE your-usr WITH PASSWORD 'your-pass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE your-db TO your-usr;"

# Configure the application
echo "DB_NAME=your-db" >> /var/www/html/your-repo/settings.py
echo "DB_USER=your-usr" >> /var/www/html/your-repo/settings.py
echo "DB_PASSWORD=your-pass" >> /var/www/html/your-repo/settings.py

# Restart the nginx service to apply changes
systemctl restart nginx

# Run the application using gunicorn
gunicorn --workers 3 --bind unix:/var/www/html/your-repo/app.sock your.app:app
