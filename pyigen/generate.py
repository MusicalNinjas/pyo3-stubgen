import textwrap
from types import FunctionType, ModuleType


def generate(f: FunctionType) -> str:
    if "\n" in f.__doc__:
        doc = f'\n    """\n{textwrap.indent(f.__doc__,"    ")}\n    """\n'
    else:
        doc = f'\n    """{f.__doc__}"""\n'
    return f"def {f.__name__}{f.__text_signature__}:{doc}"
