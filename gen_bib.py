#!/usr/bin/env python3
from pathlib import Path

incoming = Path("/Users/lachlankermode/Desktop")
outgoing = Path("/Users/lachlankermode/Dropbox/obsidian")
headers = [
    "local", "title", "author", "date", "publisher", "link", "pages"
]
divider = "---\n"

def prompt_for(string, default=None):
    text = f"{string}: " if not default else f"{string}: {default}"
    print(text, end="")
    user_input = input()
    return default if user_input == "" else user_input

def make_bib(bib):
    file = outgoing/f"bib.{bib['name']}.md"
    lines = [divider]
    for line in [f"{k}: {'' if v is None else v}\n" for k,v in bib.items() if k != 'name']:
        lines.append(line)
    lines.append(divider)

    file.unlink(missing_ok=True)
    file.touch()
    with open(file, "w+") as f:
        f.writelines(lines)

documents = incoming.glob("**/*.pdf")
for doc in documents:
    bib = {}
    bib["name"] = prompt_for("name", default=doc.stem)

    for header in headers:
        bib[header] = prompt_for(header)

    make_bib(bib)
    print()


