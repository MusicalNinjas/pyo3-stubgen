import textwrap
from types import FunctionType, ModuleType


def generate(f: FunctionType) -> str:
    return f'def {f.__name__}{f.__text_signature__}:\n    """\n{textwrap.indent(f.__doc__,"    ")}\n    """\n'
