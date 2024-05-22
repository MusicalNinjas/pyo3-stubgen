"""
`pyo3-stubgen` generates `.pyi` typing files for extension modules.

It is designed to work for extension modules created in rust with `pyo3` but should work with any compiled extension
modules which include a `__text_signature__` and optionally a `__doc__` attribute for functions.

The package containing the module to be analysed must be installed in the current virtual environment, but _does not
need to be imported_ before running `pyo3_stubgen`.

Despite flake8's recommendation to the contrary, `pyo3_stubgen` adds docstrings to the `.pyi` files so that IDEs can
provide them in hover pop-ups.

You will need to manually add the typing information to the generated files as this is not included in any of the
function attributes available and is just as dependent upon the semantics of your functions as on the technical
implementation.

Currently `pyo3_stubgen` only generates info for functions. Classes are on the to-do list.

"""

from .generate import genentry, genfile, genpyi