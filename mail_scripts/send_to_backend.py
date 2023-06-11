import sys
import os
import json
from urllib import request, parse, error

from config import ENDPOINT, WEBHOOK_URL, TOKEN

OPERATING = True

def save_last_email(email, append=False):
  mode = "a" if append else "w"
  with open("last.txt", mode) as f:
    f.write(email + "\n\n")
    f.write("---\n\n")

def pass_to_api(email):
  if ENDPOINT is None or TOKEN is None:
    return

  payload = {
    "email": email,
    "token": TOKEN,
  }
  headers = {"Content-Type": "application/json"}
  req = request.Request(ENDPOINT, data=json.dumps(payload).encode(), headers=headers, method="POST")

  try:
    response = request.urlopen(req)
    if response.status in (200, 201): return
  except error.HTTPError as e:
    if WEBHOOK_URL is None:
      return

    text = "**{}**: {}".format(e.code, e.reason)
    error_data = {
      "text": text,
      "attachments": [{
        "fallback": "(email attached)",
        "text": email,
      }]
    }

    req = request.Request(WEBHOOK_URL, data=json.dumps(error_data).encode(), headers=headers, method="POST")
    request.urlopen(req)

if __name__ == "__main__":
  if OPERATING:
    email = sys.stdin.read()
    save_last_email(email, False)
    pass_to_api(email)
