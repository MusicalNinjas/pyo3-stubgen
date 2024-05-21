# list available recipes
list:
  @just --list --justfile {{justfile()}}
  
# remove pre-built rust and python libraries (excluding .venv)
clean:
    rm -rf .pytest_cache
    rm -rf build
    rm -rf test/assets/build
    rm -rf dist
    rm -rf wheelhouse
    rm -rf .ruff_cache
    find . -depth -type d -not -path "./.venv/*" -name "__pycache__" -exec rm -rf "{}" \;
    find . -depth -type d -path "*.egg-info" -exec rm -rf "{}" \;
    find . -type f -name "*.egg" -delete
    find . -type f -name "*.so" -delete

# clean out coverage files
clean-cov:
    rm -rf pycov

# clean, remove existing .venv and rebuild the venv with pip install -e .[dev]
reset: clean clean-cov && install
    rm -rf .venv
    python -m venv .venv

# install the project and required dependecies for development & testing
install:
    .venv/bin/python -m pip install --upgrade pip 
    .venv/bin/pip install -e .[dev]
    .venv/bin/pip install tests/assets

# lint python with ruff
lint:
  - .venv/bin/ruff check .

# test python
test:
  - .venv/bin/pytest

# lint and test python
check: lint test

#run coverage analysis on python code
cov:
  pytest --cov --cov-report html:pycov --cov-report term

# serve python coverage results on localhost:8000 (doesn't run coverage analysis)
show-cov:
  python -m http.server -d ./pycov

# serve python docs on localhost:8000
docs:
  mkdocs serve