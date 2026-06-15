#!/usr/bin/env python3

from dataclasses import dataclass
from docopt import docopt
from typing import Callable
from typing import Optional
from typing import Tuple
import csv
import filetype
import hashlib
import io
import json
import logging
import os
import pathlib
import random
import sys
import time

DEFAULT_ROOT = pathlib.Path(".")
OUTPUT_FORMATS = ["just-filename", "plain", "json", "char30-delimited"]
OUTPUT_FORMATS_LIST = ", ".join(["'" + x + "'" for x in OUTPUT_FORMATS])

__doc__ = """
Usage: {0} [options] [-e <ext>]... [<DIR>]

Options:
  -h, --help                        Show this help
  <DIR>                             Directory to start descending from
                                    [DEFAULT: {1}]
  -s, --sha384-blacklist=<filename> File full of sha384s to be skipped
  -p, --path-blacklist=<filename>   File full of paths to be skipped
  -o, --output-format=<style>       {2}
                                    [DEFAULT: just-filename]
  -i, --images-only                 Only yield image files
      --only-images                 Synonym for images-only
  -v, --version                     Show version
  -e, --extension=<.txt>            Only yield files with this extension
                                    (case insensitive)
  -m, --max-tries=<max>             How many paths to fail satisfying
                                    conditions like --images-only or
                                    path-blacklist before giving up.
                                    [DEFAULT: 1000]
  -n, --info                        Print info level logging
  -d, --debug                       Print debug level logging
""".format(sys.argv[0], DEFAULT_ROOT, OUTPUT_FORMATS_LIST)


class Condition:
    def __init__(self, condition, description: str):
        self.condition = condition
        self.description =description

    def satisfied(self, x) -> bool:
        return self.condition(x)

    @staticmethod
    def true():
        return Condition(condition=lambda x: True, description="true")



class NoGoodFileFound(FileNotFoundError):
    pass

def conditions_met(conditions, testee) -> Tuple[bool, str]:
    for condition in conditions:
      if not condition.satisfied(testee):
        return (False, condition.description)
    return (True, "")

def sha384(filename):
  BLOCKSIZE = 65536
  hasher = hashlib.sha384()
  with open(filename, "rb") as f:
    buf = f.read(BLOCKSIZE)
    while len(buf) > 0:
      hasher.update(buf)
      buf = f.read(BLOCKSIZE)
  return hasher.hexdigest()


def random_file(
    *,
    root: pathlib.Path,
    file_conditions: Optional[list[Condition]],
    dir_conditions: Optional[list[Condition]]
) -> pathlib.Path:
  """
  Raises NoGoodFileFound if no regular file can be found satisfying all
  `file_conditions` whose parent directories all satisfy all `dir_conditions`
  """
  if file_conditions == None:
    file_conditions = [Condition.true()]
  if dir_conditions == None:
    dir_conditions = [Condition.true()]

  if root.is_dir():
    sat = conditions_met(dir_conditions, testee=root)
    if not sat[0]:
      raise NoGoodFileFound(f"'{root}' doesn't satisfy {sat[1]} condition")

  elif root.is_file():
    sat = conditions_met(file_conditions, testee=root)
    if not sat[0]:
      raise NoGoodFileFound(f"'{root}' doesn't satisfy {sat[1]} condition")
    return root

  else:
    raise NoGoodFileFound(f"'{root}' is not a directory or regular file")

  # Now it's a directory for sure
  logging.info(f"Searching '{root}'")
  all_items = list(root.iterdir())

  # Randomize the list
  all_items = random.sample(all_items, len(all_items))

  for dir_or_file in all_items:
    logging.debug(f"Checking '{dir_or_file}'")
    dir_or_file = root / dir_or_file
    if dir_or_file.is_file():
      logging.debug("It's a regular file")
      sat = conditions_met(testee=dir_or_file, conditions=file_conditions)
      if sat[0]:
        logging.info("Conditions met")
        return dir_or_file
    if dir_or_file.is_dir():
      logging.debug("It's a directory")
      sat = conditions_met(testee=dir_or_file, conditions=dir_conditions)
      if sat[0]:
        logging.info("Conditions met")
        return random_file(
          root=dir_or_file,
          file_conditions=file_conditions,
          dir_conditions=dir_conditions
        )

  raise NoGoodFileFound("No file satisfies all file_coditions and has parent directories all satisfy dir_conditions")


def main():
  args = docopt(__doc__, version="2.0.0")

  if args["--info"]:
    logging.basicConfig(level=logging.INFO)
  elif args["--debug"]:
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.WARNING)

  if args["--only-images"]:
    args["--images-only"] = True

  try:
    root = pathlib.Path(args["<DIR>"])
  except TypeError:
    root =  DEFAULT_ROOT

  _format = args["--output-format"]
  if _format not in OUTPUT_FORMATS:
    print("Only allowed formats are:\n  {}\nreceived '{}'".format(
        OUTPUT_FORMATS_LIST, _format))
    sys.exit(1)

  file_conditions = []
  dir_conditions = []
  blacklist = []
  if args["--sha384-blacklist"] != None:
    with open(args["--sha384-blacklist"]) as f:
      sha384_blacklist = f.read().split()
      file_conditions.append(Condition(condition=lambda x: sha384(x) not in sha384_blacklist, description="hash"))
  if args["--images-only"]:
    file_conditions.append(Condition(condition=lambda x: filetype.is_image(x), description="image"))
  if args["--path-blacklist"] != None:
    with open(args["--path-blacklist"]) as g:
      blacklist = g.read().split()
  if args["--extension"] != []:
    for extension in args["--extension"]:
      file_conditions.append(Condition(condition=lambda x: x.lower().endswith(extension.lower()), description="extension"))

  tries = 0
  max_tries = int(args["--max-tries"])
  while True:
    try:
        print(
          random_file(
            root=root,
            file_conditions=file_conditions,
            dir_conditions=dir_conditions
          )
        )
        sys.exit(0)
    except NoGoodFileFound:
        logging.info("Failed in this path, try again")
        tries += 1
        if tries >= max_tries:
          print(f"Tried {tries} times, but nothing ever matched all conditions", file=sys.stderr)
          sys.exit(2)

  """
  for _next in random_non_repeating_filenames(root,
      blacklist=blacklist, conditions=conditions):
    if _format == "just-filename":
      print(_next)
    else:
      info = {"path": _next, "sha384": sha384(_next)}
      if _format == "json":
        print(json.dumps(info))
      elif _format == "char30-delimited":
        print(chr(30).join(["path", _next, "sha384", sha384(_next)]))
      elif _format == "plain":
        print("path: {}".format(_next))
        print("sha384: {}".format(sha384(_next)))
      else:
        print(_next)
  """


if __name__ == "__main__":
  main()
