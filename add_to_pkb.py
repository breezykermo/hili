import argparse
import yaml
from pathlib import Path

def save_to_bib(data):
    with open(PKB_DIR/f"bib.{data['name']}.md", "w") as f:
        f.write(f"---\n{yaml.safe_dump(data)}---\n")

def run(args):
    save_to_bib(args)

if __name__ == "__main__":
    global PKB_DIR
    p = argparse.ArgumentParser()
    p.add_argument('pkb_dir', nargs='?', default='no_pkbdir_given')
    p.add_argument('name', nargs='?', default='no_name_given')
    p.add_argument('dturl', nargs='?', default='no_dturl_given')
    args = p.parse_args()
    if args.pkb_dir == 'no_pkbdir_given':
        print("You need to give a PKB directory")
    elif args.arg_file == 'no_argfile_given':
        print("You need to specify a file with the arguments")
    else:
        with open(args.arg_file, "r") as f:
            inner_args = yaml.safe_load(f)
        PKB_DIR = Path(args.pkb_dir)
        run(inner_args)
