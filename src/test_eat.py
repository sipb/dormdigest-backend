from utils.email_parser import eat
import traceback

filename = "./src/test_emails/2023-07-13_14-35-24.txt"
email = None

with open(filename,"r") as f:
    email = f.read()
    
try:
    eat(email)
except:
    print(traceback.format_exc())