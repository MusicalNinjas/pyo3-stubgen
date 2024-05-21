from assets.python.pypkg import testlib

from pyigen import generate


def test_imported():
    assert "multiline" in dir(testlib)

def test_multiline():
    add_pyi = '''def multiline(left, right):
    """
    Adds two numbers together.

    Has a multi-line docstring.
    """
'''
    assert generate(testlib.multiline) == add_pyi

def test_oneline():
    pyi = '''def minimal(num):
    """Has a one line docstring and implicit name and signature."""
'''
    assert generate(testlib.minimal) == pyi

def test_no_docstring():
    pyi = '''def no_docstring(num):
    ...
'''  # noqa: Q001
    assert generate(testlib.no_docstring) == pyi