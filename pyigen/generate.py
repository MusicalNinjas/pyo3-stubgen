import textwrap
from types import BuiltinFunctionType, FunctionType, ModuleType


def generate(f: FunctionType) -> str:
    if f.__doc__:
        if "\n" in f.__doc__:
            doc = f'\n    """\n{textwrap.indent(f.__doc__,"    ")}\n    """\n'
        else:
            doc = f'\n    """{f.__doc__}"""\n'
    else:
        doc = '\n    ...\n'  # noqa: Q000
    return f"def {f.__name__}{f.__text_signature__}:{doc}"

def genpyi(m: ModuleType):
    functions = [getattr(m,function) for function in dir(m)]
    contents = [generate(function) for function in functions if type(function) == BuiltinFunctionType]
    contents.insert(0, "# flake8: noqa: PYI021")
    return "\n".join(contents)