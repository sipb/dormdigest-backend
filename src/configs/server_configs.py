AVAILABLE_MODES = ["prod","testing"]
CURRENT_MODE = "prod"

if CURRENT_MODE == "prod":
    SERVER_HOST = "0.0.0.0"
    BASE_DOMAIN_URL = "https://dormdigest.mit.edu"
else:
    SERVER_HOST = "localhost"
    BASE_DOMAIN_URL = "https://dormdigest.xvm.mit.edu"

BASE_IMAGE_URL = BASE_DOMAIN_URL + "/images/"
LOCAL_IMAGE_PATH = "/Users/zxiao23/Desktop/DormDigest/dormdigest-backend/src/images/"
SERVER_PORT = 8432
SSL_KEY_FILE = "./configs/key.pem"  #replace with Let's Encrypt certs for production
SSL_CRT_FILE = "./configs/cert.pem" #replace with Let's Encrypt certs for production
