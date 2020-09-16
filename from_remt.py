import re
import os
import tempfile
from subprocess import call

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

def hili_template(quote):return f"{quote}\n---\n\n---\n\n"
def tra_parens(s): return int(s[s.find("(")+1:s.find(")")])

def run():
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
        print(edited_message)
        break
if __name__ == "__main__":
    run()
