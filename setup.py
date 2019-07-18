from setuptools import setup

setup(
  name = "random_path",
  version = "1.1.0",
  author = "John Baber-Lucero",
  author_email = "pypi@frundle.com",
  description = ("Choose random file paths with conditions"),
  license = "GPLv3",
  url = "https://github.com/jbaber/random_path",
  packages = ['random_path'],
  install_requires = ['docopt'],
  tests_require=['pytest'],
  python_requires='>=3.5, <4',
  entry_points = {
    'console_scripts': ['random-path=random_path.random_path:main'],
  }
)
