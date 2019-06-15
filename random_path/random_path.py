#!/usr/bin/env python3

import sys
import os

DEFAULT_ROOT = os.path.abspath(".")

__doc__ = """
Usage: {0} [options] <DIR>
       {0} [options]

Options:
  -v, --version          Show version
  -h, --help             Show this help
  <DIR>                  Directory to start descending from
                         [DEFAULT: {1}]
""".format(sys.argv[0], DEFAULT_ROOT)

from docopt import docopt
import random

def random_file(root, condition=None):
  if condition == None:
    condition = lambda x: True
  if not condition(root):
    return None
  if os.path.isfile(root):
    if condition(root):
      return root
    else:
      return None
  if not os.path.isdir(root):
    return None

  # Now it's a directory for sure
  all_items = os.listdir(root)
  all_items = random.sample(all_items, len(all_items))
  for dir_or_file in all_items:
    dir_or_file = os.path.join(root, dir_or_file)
    if os.path.isfile(dir_or_file) and condition(dir_or_file):
      return dir_or_file
    if os.path.isdir(dir_or_file):
      maybe = random_file(dir_or_file, condition)
      if maybe is not None:
        return maybe
  return None



def main():
  args = docopt(__doc__)
  if args["<DIR>"] == None:
    args["<DIR>"] = DEFAULT_ROOT
  print(random_file(args["<DIR>"], (lambda x: os.path.basename(x) not in ['o', 'i', 'j', 'k'])))

if __name__ == "__main__":
  main()
