import re
import os
import time
import tempfile
from subprocess import call

SERVER_URL = "https://research.forensic-architecture.org/hili"
PASSWORD = "protecttheanns"

INPUT = "/tmp/remt_anns.txt"
EDITOR = os.environ.get('EDITOR', 'nvim')
REMT_IDX = "./.remt_idx"

# NOTE: these two function copied direct from clip_to_hili.py
import requests
import json
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

def attempt_clip(clip):
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


"""
the solution here is probably to create a workflow where:
- the quotes are sanitized (and perhaps autocompleted?)
- a file is created, which is then checked/updated in vim
- when vim is closed, the clips are sent
"""

def present(quotes):
    from blessed import Terminal
    term = Terminal()
    with term.cbreak(), term.hidden_cursor():
        print(quotes)
        inp = term.inkey()

def hili_template(quote): return quote

def tra_parens(s): return int(s[s.find("(")+1:s.find(")")])

def get_clip_to_hili(url):
    def l(obj):
        tm = int(round(time.time() * 1000))
        quote = obj["quote"]
        note = obj["note"].strip("\n")
        tags = obj["tags"]
        attempt_clip({
            "time": tm,
            "quote": quote,
            "note": note,
            "tags": tags,
            "dt_href": url,
            "href": ''
        })
    return l

def run(dtUrl):
    clip_to_hili = get_clip_to_hili(dtUrl)
    with open(INPUT, 'r') as f:
        lines = f.readlines()

    ptr = 0
    page = 0
    is_content = False
    quotes = ""
    sanitized = []

    while ptr < len(lines):
        line = lines[ptr].strip()

        if ptr == len(lines)-1:
            sanitized.append(quotes)

        if is_content:
            quotes += f" {line}"

        if (re.match(r'=========(\=+)', line)):
            page = tra_parens(lines[ptr - 1])
            if page != 0: sanitized.append(quotes)
            quotes = ""
            ptr += 2
            is_content = True

        if (line == "" or line == "\n"):
            is_content = False

        ptr += 1

    clipp = '/tmp/clips.yml'
    if os.path.exists(clipp):
        os.remove(clipp)

    # this is the main part: present all the quotes as vim files to edit
    # can use registers to copy common tags, etc
    ultimate = []
    was_broke = False
    idx = 0
    start_idx = None

    if os.path.exists(REMT_IDX):
        with open(REMT_IDX, "r") as fp:
            on_disk = json.load(fp)
        start_idx = on_disk["idx"]

    for l in sanitized:
        if start_idx is not None and idx < start_idx:
            idx += 1
            continue
        initial_message = hili_template(l.strip())
        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            with open(tf.name, 'w+') as f:
                f.write(initial_message)
                f.flush()
                call([EDITOR, tf.name])

            tf.seek(0)
            edited_message = tf.readlines()

        should_skip = len(edited_message) == 0

        if len(edited_message) <= 2 and not should_skip:
            was_broke = True
            break

        # send all clips
        if not should_skip:
            ptr = 0
            current = {}
            while ptr < len(edited_message):
                if "quote" in current and "note" in current and "tags" in current:
                    clip_to_hili(current)
                    current = {}
                current["quote"] = edited_message[ptr].decode("utf-8")
                current["note"] = edited_message[ptr+1].decode("utf-8")
                current["tags"] = [x.strip() for x in edited_message[ptr+2].decode("utf-8").split(",")]
                ptr += 3
            # clip that last note!
            clip_to_hili(current)
        idx += 1

    if was_broke:
        with open(REMT_IDX, "w") as f:
            json.dump({ "idx": idx }, f)
    else:
        if os.path.exists(REMT_IDX):
            os.remove(REMT_IDX)


import argparse
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('url', nargs='?', default='no_dturl_given')
    args = p.parse_args()
    if args.url == 'no_dturl_given':
        print("You need to give a URL!!!")
    else:
        run(args.url)
