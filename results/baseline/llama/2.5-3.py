# Run the script with Python
cd /path/to/script/
python main.py

# Alternatively, you can use a Procfile for a more production-like setup (assuming you're using a PM2 or similar process manager)
cd /path/to/script/
pm2 start pm2.config.js

# To deploy to your server, simply clone the repository and run the above commands
git clone https://github.com/your-repo.git
cd your-repo
python main.py
