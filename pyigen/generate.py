"""
Generate linter hints for functions provided by external compiled modules (e.g. from rust via pyo3).

Uses the information in `__doc__` and `__text_signature__` to create suitable content for a `.pyi` file.
"""

from importlib import import_module
from pathlib import Path
import textwrap
from types import BuiltinFunctionType, FunctionType, ModuleType


def generate(function: FunctionType) -> str:
    """
    Generate the signature and docstring information for a given function.

    Arguments:
      function: the function to generate.
      
    Note:
      - function _must_ provide `function.__text_signature__`
      - If `function.__doc__` is present this will be used to generate a docstring hint

    Returns:
      A string suitable for inclusion in a `.pyi` file
    """
    if function.__doc__:
        if "\n" in function.__doc__:
            doc = f'    """\n{textwrap.indent(function.__doc__,"    ")}\n    """'
        else:
            doc = f'    """{function.__doc__}"""'
    else:
        doc = '    ...'  # noqa: Q000
    return f"def {function.__name__}{function.__text_signature__}:\n{doc}\n"

def genpyi(module: ModuleType) -> str:
    """
    Generate the contents of a `.pyi` file for a given module.

    Arguments:
      module: the module to generate

    Returns: A string suitable for use as a `.pyi` file, with the following caveats: 
    
    - Return contents are prefixed with `# flake8: noqa: PYI021`. Flake8 believes that
    "Stub files should omit docstrings, as they're intended to provide type hints, rather than documentation".
    We believe that having docstring hints in IDE is _really useful_ and linters get this info from the `.pyi` file,
    so this is a good thing to do.
    - _No type information_ is usually provided in the `__text_signature__` so you will need to add this manually 
    to the `.pyi` file afterwards.
    """
    functions = [getattr(module,function) for function in dir(module)]
    definitions = [generate(function) for function in functions if type(function) == BuiltinFunctionType]
    contents = ["# flake8: noqa: PYI021", *sorted(definitions)]
    return "\n".join(contents)

def genfile(modulename: str, outputlocation: Path) -> None:
    module = import_module(modulename)
    output = genpyi(module)
    outputfilepath = outputlocation.joinpath("/".join(modulename.split("."))).with_suffix(".pyi")
    outputfilepath.parent.mkdir(parents=True, exist_ok=True)
    outputfilepath.write_text(output)