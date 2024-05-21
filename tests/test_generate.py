from pathlib import Path

from assets.python.pypkg import testlib

from pyigen import generate, genfile, genpyi


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

def test_fullpyi():
    pyipath = Path("tests/assets/expected.pyi").resolve()
    with pyipath.open() as pyifile:
        pyi = pyifile.read()
    assert genpyi(testlib) == pyi

def test_outputfile(tmp_path):
    pyipath = Path("tests/assets/expected.pyi").resolve()
    with pyipath.open() as pyifile:
        pyi = pyifile.read()
    genfile("pypkg.testlib", tmp_path)
    outputpath = tmp_path / "pypkg/testlib.pyi"
    assert outputpath.is_file()
    with outputpath.open() as outputfile:
        output = outputfile.read()
    assert output == pyi