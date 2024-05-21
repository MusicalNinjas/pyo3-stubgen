from pathlib import Path

import pytest
from testpkg import testlib  # Used for all tests EXCEPT test_ouptutfile

from pyo3_stubgen import generate, genfile, genpyi


@pytest.fixture
def expected_pyi():
    return Path("tests/assets/expected.pyi").resolve()


def test_imported():
    """Sanity check that we have built and imported testlib."""
    assert "multiline" in dir(testlib)


def test_multiline():
    pyi = '''def multiline(left, right):
    """
    Adds two numbers together.

    Has a multi-line docstring.
    """
'''
    assert generate(testlib.multiline) == pyi


def test_oneline():
    pyi = '''def minimal(num):
    """Has a one line docstring and implicit name and signature."""
'''
    assert generate(testlib.minimal) == pyi


def test_no_docstring():
    pyi = """def no_docstring(num):
    ...
"""
    assert generate(testlib.no_docstring) == pyi


def test_fullpyi(expected_pyi):
    pyi = expected_pyi.read_text()
    assert genpyi(testlib) == pyi


def test_outputfile(tmp_path, expected_pyi):
    genfile("testpkg.testlib", tmp_path)

    expected_file = tmp_path / "testpkg/testlib.pyi"
    assert expected_file.is_file()

    expected_contents = expected_pyi.read_text()
    output = expected_file.read_text()
    assert output == expected_contents
