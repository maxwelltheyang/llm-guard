# Delete secret key file after deployment
rm -f /path/to/secret/key.py

# Clean up CI environment
docker-compose down -v
docker system prune --all --force
pip uninstall -y -r requirements.txt
