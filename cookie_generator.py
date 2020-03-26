import random, string

def generate_random_cookie():
    cookie_string = ""
    cookie_length = 32
    current_length = 0
    while current_length < cookie_length:
        cookie_string += random.choice(string.ascii_letters + string.digits)
        current_length += 1
    return cookie_string