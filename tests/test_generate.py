from assets.python.pypkg import testlib

from pyigen import generate


def test_imported():
    assert "add" in dir(testlib)

def test_add():
    add_pyi = '''def add(left, right):
    """
    Adds two numbers together

    Has a multi-line docstring
    """
'''
    assert generate(testlib.add) == add_pyi