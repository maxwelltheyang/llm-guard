import logging

# Create a logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    def __init__(self):
        self.data = {}

    def insert(self, key, value):
        try:
            self.data[key] = value
            logging.info(f"Inserted {key} with value {value}")
        except Exception as e:
            logging.error(f"Error inserting {key}: {str(e)}")

    def update(self, key, value):
        if key in self.data:
            try:
                self.data[key] = value
                logging.info(f"Updated {key} to {value}")
            except Exception as e:
                logging.error(f"Error updating {key}: {str(e)}")
        else:
            logging.warning(f"No record found for key {key}")

    def delete(self, key):
        if key in self.data:
            try:
                del self.data[key]
                logging.info(f"Deleted {key}")
            except Exception as e:
                logging.error(f"Error deleting {key}: {str(e)}")
        else:
            logging.warning(f"No record found for key {key}")

    def get(self, key):
        if key in self.data:
            try:
                return self.data[key]
            except Exception as e:
                logging.error(f"Error retrieving {key}: {str(e)}")
        else:
            logging.warning(f"No record found for key {key}")
            return None

# Usage example
db = Database()
db.insert('1', 'John')
db.update('1', 'Jane')
db.delete('1')
