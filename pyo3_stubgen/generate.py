"""
Generate linter hints for functions provided by external compiled modules (e.g. from rust via pyo3).

Uses the information in `__doc__` and `__text_signature__` to create suitable content for a `.pyi` file.
"""

import textwrap
from importlib import import_module
from pathlib import Path
from types import BuiltinFunctionType, FunctionType, ModuleType, MethodDescriptorType, BuiltinMethodType, GetSetDescriptorType
from typing import Any, Literal, LiteralString
import re

import click

FUNCTION_TYPES = (BuiltinFunctionType, MethodDescriptorType, BuiltinMethodType)
SUPPORTED_TYPES = (*FUNCTION_TYPES, type)

ParseTypesType = Literal["numpydoc", False]

def parse_numpydoc_type(typestr: str) -> str:
    """
    Parse a numpydoc type string to a python type string.
    
    Arguments:
      typestr: the numpydoc type string to parse
    
    Returns:
      A python type string
    """
    # Convert numpydoc types to python types
    typestr = typestr.replace(" or ", " | ")
    typestr = re.sub(r"{([^}]+)}", r"Literal[\1]", typestr)
    typestr = typestr.replace(", optional", " | None")
    return typestr

def parse_signature(sig: str, docstr: str | None, *, method: bool = False, 
                    parse_types: ParseTypesType = False) -> tuple[str, str | None]:
  """
  Parse the signature and docstring to generate a function signature.
  
  Arguments:
    sig: the signature string from `__text_signature__`
    docstr: the docstring from `__doc__`
    
  Returns:
    A string starting from "(" and ending before ":"
  """
  if (parse_types == "numpydoc") and docstr:
    from numpydoc.docscrape import NumpyDocString
    nd = NumpyDocString(docstr)
  else:
    nd = None
  
  args = [x.strip() for x in sig.strip(" ()").split(", ")]
  
  decorator: str | None = None
  if method:
    # We presume static, and change when a $self or $cls is present.
    decorator = "@staticmethod"
  
  newargs = []
  for argstr in args:
    spl = argstr.split("=")
    argname = spl[0]
    if argname == "$self":
      argname = "self"
      if method:
        decorator = None
    elif argname == "$cls":
      argname = "cls"
      if method:
        decorator = "@classmethod"
    argdef = spl[1] if len(spl) == 2 else None
    
    argtype = None
    if nd and (pars := nd["Parameters"]):
      for par in pars:
        if (par.name == argname) and par.type:
          argtype = parse_numpydoc_type(par.type)
          break
        
    newargs.append(argname + (f": {argtype}" if argtype else "") + (f" = {argdef}" if argdef else ""))
  
  rettype = None
  if nd:
    r = nd["Returns"]
    if (len(r) == 1) and (rt := r[0].type):
      rettype = parse_numpydoc_type(rt)
    elif len(r) > 1:
      rettypes = []
      for rt in r:
        if rt.type:
          rettypes.append(parse_numpydoc_type(rt.type))
        else:
          rettypes.append("Any")
      rettype: LiteralString = f"tuple[{', '.join(rettypes)}]"
    elif len(r) == 0:
      rettype = "None"


  ret = f" -> {rettype}" if rettype else ""

  return f"({', '.join(newargs)}){ret}", decorator

  

def gen_function_entry(function: FunctionType | MethodDescriptorType | BuiltinFunctionType, 
                       method: bool = False, parse_types: ParseTypesType = False) -> str:
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
        doc = "    ..."  # noqa: Q000

    signature, decorator = parse_signature(function.__text_signature__, function.__doc__,
                                                            method=method, parse_types=parse_types)

    s = f"def {function.__name__}{signature}:\n{doc}\n"
    
    return f"{decorator}\n{s}" if decorator is not None else s

def gen_property_entry(descriptor: GetSetDescriptorType, *, parse_types: ParseTypesType = False) -> str:
    proptype: str | None = None
    if descriptor.__doc__:
        if "\n" in descriptor.__doc__:
            doc = f'    """\n{textwrap.indent(descriptor.__doc__,"    ")}\n    """'
        else:
            doc = f'    """{descriptor.__doc__}"""'
        if parse_types == 'numpydoc':
          m = re.match(r"^([^:]+):", descriptor.__doc__)
          if m:
              proptype = m[1].strip()
    else:
        doc = "    ..."  # noqa: Q000
    
    ret = f"-> {proptype}" if proptype is not None else ""
    valtypestr = f": {proptype}" if proptype is not None else ""
    
    return (f"@property\ndef {descriptor.__name__}(self){ret}:\n{doc}\n\n"
            f"@{descriptor.__name__}.setter\ndef {descriptor.__name__}(self, value{valtypestr}) -> None:\n    ...\n")

def gen_class_entry(cls: type, *, parse_types: ParseTypesType = False) -> str:
    """
    Generate the signature and docstring information for a given class.

    Arguments:
      cls: the class to generate

    Returns:
      A string suitable for inclusion in a `.pyi` file
    """
    dir_contents = [getattr(cls, function) for function in dir(cls)]
    
    methods: list[str] = []
    
    for dir_entry in dir_contents:
        if (type(dir_entry) in (MethodDescriptorType, BuiltinMethodType) 
            and hasattr(dir_entry, "__text_signature__") 
            and not dir_entry.__name__.startswith("__")):
            methods.append(textwrap.indent(gen_function_entry(dir_entry, method=True, parse_types=parse_types), "    "))
        elif (type(dir_entry) == GetSetDescriptorType and not dir_entry.__name__.startswith("__")):
            methods.append(textwrap.indent(gen_property_entry(dir_entry, parse_types=parse_types), "    "))        

    if cls.__doc__:
        if "\n" in cls.__doc__:
            doc = f'    """\n{textwrap.indent(cls.__doc__,"    ")}\n    """'
        else:
            doc = f'    """{cls.__doc__}"""'
    elif not methods:
        doc = "    ..."  # noqa: Q000
    else:
        doc = ""
    doc += "\n" + "\n".join(methods)
    return f"class {cls.__name__}:\n{doc}\n"

def genentry(obj: Any, *, parse_types: ParseTypesType = False) -> str:
    """
    Generate the signature and docstring information for a given function or class.

    Arguments:
      obj: the object to use to generate the entry

    Note:
      - functions _must_ provide `function.__text_signature__`
      - If `function.__doc__` is present this will be used to generate a docstring hint

    Returns:
      A string suitable for inclusion in a `.pyi` file
    """
    if type(obj) in FUNCTION_TYPES:
        return gen_function_entry(obj, parse_types = parse_types)
    if type(obj) == type:
        return gen_class_entry(obj, parse_types = parse_types)
    msg = f"Unsupported type {type(obj)}"
    raise ValueError(msg)

def genpyi(module: ModuleType, *, parse_types: ParseTypesType = False) -> str:
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
    objs = [getattr(module, obj) for obj in dir(module)]
    definitions = [genentry(obj, parse_types=parse_types) for obj in objs if type(obj) in SUPPORTED_TYPES]
    contents = ["# flake8: noqa: PYI021", *sorted(definitions)]
    return "\n".join(contents)

def genfile(modulename: str, outputlocation: Path, *, parse_types: ParseTypesType = False) -> None:
    """
    Generate a `.pyi` file for `modulename` and store it under the project root `outputlocation`.

    Arguments:
      modulename: The _fully qualified_ module name: e.g. `pypkg.rustlib`.
      outputlocation: The `Path` to the _project root_ where the resulting file should be saved. Note: 
      *, parse_types: 

    Example:
      `genfile("pypkg.rustlib", Path("python"))` will result in the creation of `./python/pypkg/rustlib.pyi`

    Note:
      - the package containing modulename must be installed and available for import such as
      `from pypkg.rustlib import ...` but does NOT have to be imported already.
      - the output file will be stored in a subdirectory based upon the fully qualified module name.
    """
    module = import_module(modulename)
    output = genpyi(module, parse_types=parse_types)
    outputfile = outputlocation.joinpath("/".join(modulename.split("."))).with_suffix(".pyi")
    outputfile.parent.mkdir(parents=True, exist_ok=True)
    outputfile.write_text(output)

# Dedicated shim function to allow for specific formatting and contents of docstrings (IDE & API docs vs. CLI --help)
@click.command()
@click.argument("modulename")
@click.argument("outputlocation", type=click.Path(file_okay=False, resolve_path=True, path_type=Path))
@click.option("--parse-numpydoc/--no-parse-numpydoc", "-n/", default=False, help="Parse the types from the docstring")
def _stubgen(modulename: str, outputlocation: Path, parse_numpydoc: bool) -> None:  # noqa: D417
    """
    Generate a `.pyi` file for MODULENAME and store it under the project root OUTPUTLOCATION.

    Arguments:
    
      MODULENAME: The _fully qualified_ module name: e.g. `pypkg.rustlib`.

          Note: the package containing modulename must be installed in your working environment.

      OUTPUTLOCATION: The path to the project root where the resulting file should be saved.

          Note: the output file will be stored in a subdirectory based upon the fully qualified module name.

    Example:

      `pyo3-stubgen pypkg.rustlib python` creates `./python/pypkg/rustlib.pyi`
    """  # noqa: D412
    
    genfile(modulename, outputlocation, parse_types="numpydoc" if parse_numpydoc else False)