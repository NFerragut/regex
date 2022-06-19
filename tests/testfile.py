"""testfile.py -- Manage test files for unit tests."""

import locale
import os


def check_contents(filename, contents):
    """Check that the file contains the expected content."""
    encoding = locale.getpreferredencoding(False)
    with open(filename, 'rt', encoding=encoding) as fin:
        text = fin.read()
    assert text == contents


def create_file(filename, contents=''):
    """Create a file with the specified contents."""
    encoding = locale.getpreferredencoding(False)
    with open(filename, 'wt', encoding=encoding) as fout:
        fout.write(contents)


def remove_file(filename):
    """Remove the file if it exists."""
    if os.path.isfile(filename):
        os.remove(filename)
    assert not os.path.isfile(filename)
