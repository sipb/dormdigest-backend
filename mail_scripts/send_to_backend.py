"""
Forward the email to backend at the correct endpoint
"""

import sys
import os
import requests

ENDPOINT = f""

def save_last_email(email, append=False):
  mode = "a" if append else "w"
  with open("last.txt", mode) as f:
    f.write(email)

if __name__ == "__main__":
  email = sys.stdin.read()
  save_last_email(email)


