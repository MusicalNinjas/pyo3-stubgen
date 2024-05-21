from assets.python.pypkg import testlib

from pyigen import generate


def test_imported():
    assert "add" in dir(testlib)

def test_multiline():
    add_pyi = '''def add(left, right):
    """
    Adds two numbers together

    Has a multi-line docstring
    """
'''
    assert generate(testlib.add) == add_pyi

def test_oneline():
    pyi = '''def double(num):
    """Has a one line docstring and one argument"""
'''
    assert generate(testlib.double) == pyi