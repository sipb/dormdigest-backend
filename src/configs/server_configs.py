AVAILABLE_MODES = ["prod","testing","dev"]
CURRENT_MODE = "prod"

if CURRENT_MODE == "prod":
    SERVER_HOST = "0.0.0.0"
    BASE_DOMAIN_URL = "https://dormdigest.mit.edu"
elif CURRENT_MODE == "testing":
    SERVER_HOST = "0.0.0.0"
    BASE_DOMAIN_URL = "https://dormdigest.xvm.mit.edu"
else:
    SERVER_HOST = "localhost"
    BASE_DOMAIN_URL = "https://localhost"

BASE_IMAGE_URL = BASE_DOMAIN_URL + "/images/"
LOCAL_IMAGE_PATH = "./images/"
SERVER_PORT = 8432
SSL_KEY_FILE = "./configs/key.pem"  #replace with Let's Encrypt certs for production
SSL_CRT_FILE = "./configs/cert.pem" #replace with Let's Encrypt certs for production
