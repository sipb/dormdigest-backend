"""
Forward the email to backend at the correct endpoint
"""

import sys
import os
import requests

from config import ENDPOINT, WEBHOOK_URL, TOKEN

def save_last_email(email, append=False):
  mode = "a" if append else "w"
  with open("last.txt", mode) as f:
    f.write(email)

def pass_to_api(email):
  if ENDPOINT is None or TOKEN is None:
    return

  payload = {
    "email": email,
    "token": TOKEN,
  }
  response = requests.post(ENDPOINT, json=payload)
  if response.status_code == 200: return

  if WEBHOOK_URL is None: return

  error = {
    "text": f"{response.status_code}: {response.content}",
    "attachments": [{
      "fallback": "(email attached)",
      "text": email,
    }]
  }

  requests.post(WEBHOOK_URL, json=error)

if __name__ == "__main__":
  email = sys.stdin.read()
  save_last_email(email)
  pass_to_api(email)
