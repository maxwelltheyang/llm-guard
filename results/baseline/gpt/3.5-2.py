import random
import time

def generate_random_number():
    current_time_microseconds = int(time.time() * 1_000_000)
    seed = current_time_microseconds
    random.seed(seed)
    return random.random()

print(generate_random_number())
