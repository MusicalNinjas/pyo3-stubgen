# Overview

`pyo3-stubgen` generates `.pyi` typing files for extension modules which were written in rust with pyo3.

It is designed to work for extension modules created in rust with pyo3 but should work with any compiled extension
modules which include a `__text_signature__` and optionally a `__doc__` attribute for functions.

Despite flake8's recommendation to the contrary, `pyo3_stubgen` adds docstrings to the `.pyi` files so that IDEs can
provide them in hover pop-ups.

!!! note
    You will need to manually add the typing information to the generated files as this is not included in any of the function attributes available and is just as dependent upon the semantics of your functions as on the technical implementation.

Currently `pyo3_stubgen` only generates info for functions. Classes are on the to-do list.

## Installation

Install via pip:

```sh
(.venv)/projectroot$ pip install pyo3-stubgen
```

## Usage

Easiest from the command line:

```sh
(.venv)/projectroot$ pyo3-stubgen MODULENAME OUTPUTLOCATION
```

??? tip "`pyo3-stubgen --help`"
    ```text
    Generate a `.pyi` file for MODULENAME and store it under the project root OUTPUTLOCATION.

    Arguments:
    
      MODULENAME: The _fully qualified_ module name: e.g. `pypkg.rustlib`.

          Note: the package containing modulename must be installed in your working environment.

      OUTPUTLOCATION: The path to the project root where the resulting file should be saved.

          Note: the output file will be stored in a subdirectory based upon the fully qualified module name.

    Example:

      `pyo3-stubgen pypkg.rustlib python` creates `./python/pypkg/rustlib.pyi`
    ```

Alternatively via the python API. See [the docs](https://musicalninjas.github.io/pyo3-stubgen) for more details.

??? note "Changes"
    - v0.3.0: renamed shell command to `pyo3-stubgen`

## Issues, Bugs, Ideas

Please contribute on github [MusicalNinjas/pyo3-stubgen](https://github.com/MusicalNinjas/pyo3-stubgen).
