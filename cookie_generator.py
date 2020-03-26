import random, string

def generate_random_cookie(length=32):
    cookie_string = ""
    cookie_length = length
    current_length = 0
    while current_length < cookie_length:
        cookie_string += random.choice(string.ascii_letters + string.digits)
        current_length += 1
    return cookie_string