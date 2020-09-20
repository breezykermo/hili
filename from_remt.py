import re
import os
import tempfile
from subprocess import call
from typing import List

INPUT = "/tmp/remt_anns.txt"
EDITOR = os.environ.get('EDITOR', 'nvim')

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

def get_clip_to_hili(dtUrl):
    def l(obj):
        quote = obj["quote"]
        note = obj["note"]
        tags = obj["tags"]
        # TODO: POST request
        print(quote, note, tags, dtUrl)
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

    ultimate = []
    for l in sanitized:
        initial_message = hili_template(l.strip())
        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            with open(tf.name, 'w+') as f:
                f.write(initial_message)
                f.flush()
                call([EDITOR, tf.name])

            tf.seek(0)
            edited_message = tf.readlines()
        ultimate += edited_message
        break


    ptr = 0
    current = {}
    import pdb; pdb.set_trace()
    while ptr < len(ultimate):
        if ultimate[ptr].decode("utf-8") == "\n":
            clip_to_hili(current)
            current = {}
            ptr += 1
        current["quote"] = ultimate[ptr].decode("utf-8")
        current["note"] = ultimate[ptr+1].decode("utf-8")
        current["tags"] = [x.strip() for x in ultimate[ptr+2].decode("utf-8").split(",")]
        ptr += 3

import argparse
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('url', nargs='?', default='no_dturl_given')
    args = p.parse_args()
    if args.url == 'no_dturl_given':
        print("You need to give a URL!!!")
    else:
        run(args.url)
