import random
import time

seed = int(time.time() * 1000) + (int(time.perf_counter() * 1000) % 1000)
random.seed(seed, version=2)
