"""
Generate linter hints for functions provided by external compiled modules (e.g. from rust via pyo3).

Uses the information in `__doc__` and `__text_signature__` to create suitable content for a `.pyi` file.
"""

import textwrap
from importlib import import_module
from pathlib import Path
from types import BuiltinFunctionType, FunctionType, ModuleType

import click


def genentry(function: FunctionType) -> str:
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
    definitions = [genentry(function) for function in functions if type(function) == BuiltinFunctionType]
    contents = ["# flake8: noqa: PYI021", *sorted(definitions)]
    return "\n".join(contents)

def genfile(modulename: str, outputlocation: Path) -> None:
    """
    Generate a `.pyi` file for `modulename` and store it under the project root `outputlocation`.

    Arguments:
      modulename: The _fully qualified_ module name: e.g. `pypkg.rustlib`.
      outputlocation: The `Path` to the _project root_ where the resulting file should be saved. Note: 

    Example:
      `genfile("pypkg.rustlib", Path("python"))` will result in the creation of `./python/pypkg/rustlib.pyi`

    Note:
      - the package containing modulename must be installed and available for import such as
      `from pypkg.rustlib import ...` but does NOT have to be imported already.
      - the output file will be stored in a subdirectory based upon the fully qualified module name.
    """
    module = import_module(modulename)
    output = genpyi(module)
    outputfile = outputlocation.joinpath("/".join(modulename.split("."))).with_suffix(".pyi")
    outputfile.parent.mkdir(parents=True, exist_ok=True)
    outputfile.write_text(output)

# Dedicated shim function to allow for specific formatting and contents of docstrings (IDE & API docs vs. CLI --help)
@click.command()
@click.argument("modulename")
@click.argument("outputlocation", type=click.Path(file_okay=False, resolve_path=True, path_type=Path))
def _stubgen(modulename: str, outputlocation: Path) -> None:  # noqa: D417
    """
    Generate a `.pyi` file for MODULENAME and store it under the project root OUTPUTLOCATION.

    Arguments:
    
      MODULENAME: The _fully qualified_ module name: e.g. `pypkg.rustlib`.

          Note: the package containing modulename must be installed in your working environment.

      OUTPUTLOCATION: The path to the project root where the resulting file should be saved.

          Note: the output file will be stored in a subdirectory based upon the fully qualified module name.

    Example:

      `stubgen pypkg.rustlib python` creates `./python/pypkg/rustlib.pyi`
    """  # noqa: D412
    genfile(modulename, outputlocation)