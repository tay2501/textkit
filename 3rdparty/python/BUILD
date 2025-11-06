# Third-party Python dependencies
# Pants will use the dependencies defined in pyproject.toml
#
# This BUILD file allows Pants to track and manage third-party dependencies
# while preserving the existing pyproject.toml as the source of truth

# Reference to pyproject.toml for dependency definitions
python_requirements(
    name="reqs",
    source="requirements.txt",
    resolve="python-default",
)

# Note: Initially, this uses a requirements.txt file that we'll generate
# from pyproject.toml. Future improvements can integrate directly with
# pyproject.toml using the python_requirements(source="pyproject.toml") syntax
