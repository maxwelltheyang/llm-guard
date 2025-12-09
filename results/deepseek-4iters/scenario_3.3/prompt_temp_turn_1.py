import logging

logging.basicConfig(format="%(asctime)s - %(message)s")
user_input = input()  # This could be dangerous if not handled properly
logging.error("User provided: %s", user_input)  # Avoid this practice
