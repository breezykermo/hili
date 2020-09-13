import sys
import requests
import time

SERVER_URL = "https://research.forensic-architecture.org/hili"
PASSWORD = "protecttheanns"

# applescript is a pain, esp with text characters; so writing args to a file is easiest.
ARGS = "/tmp/args.txt"


def run():
    with open(ARGS, 'r') as f:
        data = f.readlines()
    tm = int(round(time.time() * 1000))

    idx = 0
    quote = ""
    while data[idx] != "*--ENDQUOTE--*\n" and idx < len(data):
        quote += data[idx]
        idx += 1
    idx += 1

    note = data[idx].rstrip("\n").strip()
    tags = data[idx + 1].rstrip("\n").strip().split(",")
    url = data[idx + 2].rstrip("\n").strip()

    body = {
        "time": tm,
        "quote": quote,
        "note": note,
        "tags": tags,
        "dt_href": url,
        "href": ''
    }
    r = requests.post(
        SERVER_URL,
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authentication": PASSWORD,
        },
        json = body
    )

    print(body)
    print(r.content)



if __name__ == "__main__":
    run()
