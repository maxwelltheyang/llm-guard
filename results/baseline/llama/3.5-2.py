import random
import time

def seeded_random():
    seed = int(time.time() * 1e6)  # get current time in microseconds
    return random.Random(seed)

# example usage:
random_generator = seeded_random()
print(random_generator.random())
