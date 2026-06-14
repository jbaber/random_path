#!/usr/bin/env python3

from docopt import docopt
import csv
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
  -v, --version                     Show version
  -e, --extension=<.txt>            Only yield files with this extension
                                    (case insensitive)

  -n, --info                        Print info level logging
  -d, --debug                       Print debug level logging
""".format(sys.argv[0], DEFAULT_ROOT, OUTPUT_FORMATS_LIST)


class NoGoodFileFound(FileNotFoundError):
    pass


def sha384(filename):
  BLOCKSIZE = 65536
  hasher = hashlib.sha384()
  with open(filename, "rb") as f:
    buf = f.read(BLOCKSIZE)
    while len(buf) > 0:
      hasher.update(buf)
      buf = f.read(BLOCKSIZE)
  return hasher.hexdigest()


def random_non_repeating_filenames(root, *, blacklist=None,
    conditions=None):
  if conditions == None:
    conditions = []
  if blacklist != None:
    conditions.append(lambda x: x not in blacklist)

  # TODO Consider how large this gets and do write
  # to disk if it gets too big or do some other intelligent
  # optimizations
  already_yielded = []
  new_filename = random_file(root,
      file_condition = lambda x:
        x not in already_yielded and
        all([condition(x) for condition in conditions])
  )
  while new_filename != None:
    already_yielded.append(new_filename)
    yield new_filename
    new_filename = random_file(root,
        file_condition = lambda x:
          x not in already_yielded and
          all([condition(x) for condition in conditions])
    )


def conditions_met(*, testee, conditions) -> bool:
    for condition in conditions:
        if not condition(testee):
            return False
    return True


def random_file(
    *,
    root: pathlib.Path,
    file_conditions=None,
    dir_conditions=None
) -> pathlib.Path:
  """
  Raises NoGoodFileFound if no regular file can be found satisfying all
  `file_conditions` whose parent directories all satisfy all `dir_conditions`
  """
  if file_conditions == None:
    file_conditions = [lambda x: True]
  if dir_conditions == None:
    dir_conditions = [lambda x: True]
  if not conditions_met(testee=root, conditions=dir_conditions):
    raise NoGoodFileFound(f"'{root}' doesn't satisfy all dir_conditions")
  if root.is_file():
    if conditions_met(testee=root, conditions=file_conditions):
      return root
    else:
      raise NoGoodFileFound(f"'{root}' that doesn't satisfy all file_conditions")
  if not root.is_dir():
    return NoGoodFileFound(f"'{root}' is not a directory or regular file")

  # Now it's a directory for sure
  logging.info(f"Searching '{root}'")
  all_items = list(root.iterdir())

  # Randomize the list
  all_items = random.sample(all_items, len(all_items))
  for dir_or_file in all_items:
    logging.debug(f"Checking '{dir_or_file}'")
    dir_or_file = root / dir_or_file
    if dir_or_file.is_file():
      logging.info("It's a regular file")
      if conditions_met(testee=dir_or_file, conditions=file_conditions):
        logging.info("Conditions met")
        return dir_or_file
    if dir_or_file.is_dir():
        logging.debug("It's a directory")
        if conditions_met(testee=dir_or_file, conditions=dir_conditions):
          logging.info("Conditions met")
          return random_file(
            root=dir_or_file,
            file_conditions=file_conditions,
            dir_conditions=dir_conditions
          )

  raise NoGoodFileFound("No file satisfies all file_coditions and has parent directories all satisfy dir_conditions")


def main():
  args = docopt(__doc__, version="1.2.0")

  if args["--info"]:
    logging.basicConfig(level=logging.INFO)
  elif args["--debug"]:
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.WARNING)

  try:
    root = pathlib.Path(args["<DIR>"])
  except TypeError:
    root =  DEFAULT_ROOT

  _format = args["--output-format"]
  if _format not in OUTPUT_FORMATS:
    print("Only allowed formats are:\n  {}\nreceived '{}'".format(
        OUTPUT_FORMATS_LIST, _format))
    exit(1)

  file_conditions = []
  blacklist = []
  if args["--sha384-blacklist"] != None:
    with open(args["--sha384-blacklist"]) as f:
      sha384_blacklist = f.read().split()
      file_conditions.append(lambda x: sha384(x) not in sha384_blacklist)
  if args["--path-blacklist"] != None:
    with open(args["--path-blacklist"]) as g:
      blacklist = g.read().split()
  if args["--extension"] != []:
    for extension in args["--extension"]:
      file_conditions.append(lambda x: x.lower().endswith(extension.lower()))

  while True:
    try:
        print(random_file(root=root, file_conditions=file_conditions))
        sys.exit(0)
    except NoGoodFileFound:
        logging.info("Failed in this path, try again")
        time.sleep(.1)

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
