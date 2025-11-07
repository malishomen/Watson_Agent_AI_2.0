import random

def generate_random_number(min_val=1, max_val=1000):
    return random.randint(min_val, max_val)

if __name__ == "__main__":
    print(generate_random_number())