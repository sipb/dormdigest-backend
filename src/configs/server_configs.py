import os
from enum import Enum

'''
There are three available modes:

- "prod" - to be used on official, production DormDigest server
- "testing" - to be used on XVM instance to test out new features
- "dev" - to be used locally by project developers

'''
class AVAILABLE_MODES(Enum):
    PROD = "PROD"
    TESTING = "TESTING"
    DEV = "DEV"

CURRENT_MODE = AVAILABLE_MODES.DEV #By default, we have it set to local development.
                                   #For production and testing environments, you
                                   #should use `run_prod.sh` and `run_testing.sh`
                                   #which will set an environment variable that
                                   #overrides this config.

override_mode = os.getenv('CURRENT_MODE') #Use environment variable to change mode
if override_mode and override_mode in [e.value for e in AVAILABLE_MODES]:
    CURRENT_MODE = AVAILABLE_MODES(override_mode)

'''
Breakdown of variable config options:

- SERVER_HOST: Where to serve FastAPI server. 
    * "localhost" means only accessible by this computer, 
    * "0.0.0.0" means listening on all ports (accessible by anyone else in the network)
- ALLOWED_ORIGINS: Define the CORS list of endpoints which are allowed to talk to this server
    * Only affect browsers
- USE_HTTPS: Whether to use HTTP/HTTPS
    * True => HTTPS (Uses the key.pem and cert.pem in the `configs` folder)
    * False => HTTP
- USE_REDIS_CACHING: Whether to use Redis server (if available)
    * True => If Redis service is running, use it for caching
    * False => Regardless if Redis is available or not, DO NOT cache any results
- BASE_IMAGE_URL: URL where we can find the events images
    * For `prod` and `testing`, it is the Nginx endpoing that is serving files statically
    * For `dev`, it is the backend FastAPI endpoint serving static files
'''

LOCAL_IMAGE_PATH = "./images/" #Path to where images should be stored locally after extraction
SERVER_PORT = 8432
SSL_KEY_FILE = "./configs/key.pem"  #replace with Let's Encrypt certs for production
SSL_CRT_FILE = "./configs/cert.pem" #replace with Let's Encrypt certs for production

if CURRENT_MODE == AVAILABLE_MODES.PROD:
    SERVER_HOST = "0.0.0.0"
    ALLOWED_ORIGINS = ["https://dormdigest.mit.edu"]
    USE_HTTPS = True
    USE_REDIS_CACHING = True
    BASE_IMAGE_URL = "https://dormdigest.mit.edu/images/"
elif CURRENT_MODE == AVAILABLE_MODES.TESTING:
    SERVER_HOST = "0.0.0.0"
    ALLOWED_ORIGINS = ["https://dormdigest.xvm.mit.edu"]
    USE_HTTPS = True
    USE_REDIS_CACHING = True
    BASE_IMAGE_URL = "https://dormdigest.xvm.mit.edu/images/"
else: #By default, AVAILABLE_MODES.DEV
    SERVER_HOST = "localhost"
    ALLOWED_ORIGINS = ["http://localhost:3000","https://localhost:3000"]
    USE_HTTPS = False
    USE_REDIS_CACHING = False # By default, don't use caching even if Redis is available.
                              # This is to avoid situations where cache data becomes stale, 
                              # which is a common side-effect when you're modifying the database
                              # often during development
    if USE_HTTPS:
        BASE_IMAGE_URL = f"https://localhost:{SERVER_PORT}/images/"
    else:
        BASE_IMAGE_URL = f"http://localhost:{SERVER_PORT}/images/"

