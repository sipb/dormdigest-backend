import random
import string

# Note: It's very important when using random to call
# random.SystemRandom().choice instead of random.choice. 
# This is because the PRNG in random is not crytographically secure

def random_id_string(stringLength=6):
    """Generate a random string of letters and digits"""
    available_characters = string.ascii_lowercase + string.digits
    return ''.join(random.SystemRandom().choice(available_characters) for i in range(stringLength))

def random_number_string(stringLength=6):
    """Generate a random string of letters and digits """
    available_characters = string.digits
    return ''.join(random.SystemRandom().choice(available_characters) for i in range(stringLength))

def generate_API_token(length=20):
    """Generate a random token to be used for API authentication
    """
    characters = list(string.hexdigits[:16])
    return ''.join(random.SystemRandom().choice(characters) for i in range(length))
