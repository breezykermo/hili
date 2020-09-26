import sys
import os
import json
import requests
import time

SERVER_URL = "https://research.forensic-architecture.org/hili"
PASSWORD = "protecttheanns"

# applescript is a pain, esp with text characters; so writing args to a file is easiest.
ARGS = "/tmp/args.txt"
CACHE = "./cached_clips.json" # not in temp so it isn't removed

def send(body):
    requests.post(
        SERVER_URL,
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authentication": PASSWORD,
        },
        json = body
    )

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

    clip = {
        "time": tm,
        "quote": quote,
        "note": note,
        "tags": tags,
        "dt_href": url,
        "href": ''
    }

    try:
        send(clip)

        # if clip is successful, flush all cached
        if os.path.exists(CACHE):
            with open(CACHE, "r") as c:
                cached_clips = [json.loads(l) for l in c.readlines()]

        for cached_clip in cached_clips:
            send(cached_clip)

        os.remove(CACHE)

    # TODO: only catch the specifics
    except requests.ConnectionError:
        is_first = not os.path.exists(CACHE)
        with open(CACHE, "a") as cache:
            if not is_first: cache.write("\n")
            json.dump(clip, cache)
        print("No internet connection, dumped to cache")



if __name__ == "__main__":
    run()
