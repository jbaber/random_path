from random_path import random_path as rp
import os

def test_random_file(tmp_path):
  # a
  # └── b
  #     ├── c
  #     │   ├── d
  #     │   │   └── e
  #     │   │       └── f
  #     │   │           ├── g
  #     │   │           │   └── h
  #     │   │           │       ├── i
  #     │   │           │       │   └── j
  #     │   │           │       ├── s
  #     │   │           │       └── t
  #     │   │           └── q
  #     │   ├── k
  #     │   │   └── l
  #     │   │       ├── m
  #     │   │       │   └── n
  #     │   │       └── r
  #     │   └── o
  #     └── p
  d = tmp_path
  for letter in "a/b/c/d/e/f/g/h/i/j".split("/"):
    d = d / letter
    d.mkdir()
  for letter in "st":
    d = tmp_path / "a/b/c/d/e/f/g/h" / letter
    d.mkdir()
  d = tmp_path / "a/b/c/d/e/f" / "q"
  d.mkdir()
  d = tmp_path / "a/b/c"
  for letter in "klm":
    d = d / letter
    d.mkdir()
  d = tmp_path / "a/b/c/k/l" / "r"
  d.mkdir()
  d = tmp_path / "a/b/c" / "o"
  d.mkdir()
  d = tmp_path / "a/b" / "p"
  d.mkdir()

  for path in [
    "a/b/c/k/l/m/n",
    "a/b/c/k/l/r",
    "a/b/c/d/e/f/g/h/s",
    "a/b/c/d/e/f/g/h/t",
  ]:
    d = tmp_path / path
    d.touch()
  import pdb; pdb.set_trace()
