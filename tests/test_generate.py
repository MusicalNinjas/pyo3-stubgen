from assets.python.pypkg import testlib

def test_imported():
    assert 'add' in dir(testlib)