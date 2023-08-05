import sys
import os
import json
from urllib import request, error
from datetime import datetime
from pathlib import Path

from config import ENDPOINT, WEBHOOK_URL, TOKEN

OPERATING = True

_headers = {"Content-Type": "application/json"}

def save_last_email(email):
  filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.txt")
  filepath = Path("./saved") / filename
  with open(filepath, "w") as f:
    f.write(email + "\n")

  link = "mail_scripts/saved/" + filename
  return link

def send_error_to_mattermost(http_error):
  link = save_last_email(email)

  if WEBHOOK_URL is None:
      return

  text = "**{}**: {}\n\nEmail was saved to: {}".format(http_error.code, http_error.reason, link)
  data = {"text": text}

  req = request.Request(WEBHOOK_URL, data=json.dumps(data).encode(), headers=_headers, method="POST")
  request.urlopen(req)

def pass_to_api(email):
  if ENDPOINT is None or TOKEN is None:
    return

  payload = {
    "email": email,
    "token": TOKEN,
  }
  req = request.Request(ENDPOINT, data=json.dumps(payload).encode(), headers=_headers, method="POST")

  try:
    response = request.urlopen(req)
    if response.status in (200, 201):
      save_last_email(email)
      return
  except error.HTTPError as e:
    send_error_to_mattermost(e)

if __name__ == "__main__":
  if OPERATING:
    email = sys.stdin.read()
    pass_to_api(email)
