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
  root = str(tmp_path)
  os.makedirs(os.path.join(root, "a/b/c/d/e/f/g/h/i/j"))
  os.makedirs(os.path.join(root, "a/b/c/d/e/f/q"))
  os.makedirs(os.path.join(root, "a/b/c/k/l/m"))
  os.makedirs(os.path.join(root, "a/b/c/o"))
  os.makedirs(os.path.join(root, "a/b/c/p"))

  filenames = [
    "a/b/c/k/l/m/n",
    "a/b/c/k/l/r",
    "a/b/c/d/e/f/g/h/s",
    "a/b/c/d/e/f/g/h/t",
  ]
  abs_paths = [os.path.join(root, x) for x in filenames]

  for abs_path in abs_paths:
    assert not os.path.exists(abs_path)
    open(abs_path, "w").close()
    assert os.path.exists(abs_path)

  filenames = []
  for i in range(7):
    new = rp.random_file(root, file_condition = lambda x: x not in filenames)
    if new != None:
      filenames.append(new)

  assert set(filenames) == set(abs_paths)
