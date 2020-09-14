from blessed import Terminal

INPUT = "/Users/lachlankermode/code/pkb/harvey.txt"

"""
the solution here is probably to create a workflow where:
- the quotes are sanitized (and perhaps autocompleted?)
- a file is created, which is then checked/updated in vim
- when vim is closed, the clips are sent
"""

term = Terminal()

def present(quotes):
    with term.cbreak(), term.hidden_cursor():
        print(quotes)
        inp = term.inkey()

def hili_template(quote):
    return f"- q: {quote}\n\tn:\n\tt:\n"

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

        if is_content:
            quotes += f" {line}"

        if (line == "=========="):
            if page != 0: sanitized.append(quotes)
            quotes = ""
            page += 1
            ptr += 2
            is_content = True

        if (line == ""):
            is_content = False

        ptr += 1

    with open('/tmp/clips.yml', 'w+') as f:
        for l in sanitized:
            f.write(hili_template(l.strip()))

if __name__ == "__main__":
    run()
