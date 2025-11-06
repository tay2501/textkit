# Root BUILD file for Textkit project
# Pants Build integration with Polylith Architecture
#
# This BUILD file provides top-level declarations for the entire workspace.
# Individual components, bases, and projects will have their own BUILD files
# for fine-grained dependency management.

# Python source roots for the entire project
# This ensures Pants recognizes our Polylith structure
python_sources(
    name="root",
    sources=["**/*.py"],
    # Exclude specific directories that should not be treated as source
    skip_ruff=True,
    skip_mypy=True,
)

# Pyproject.toml and other config files as resources
# This makes them available to tools that need them
files(
    name="config_files",
    sources=[
        "pyproject.toml",
        "workspace.toml",
        "mypy.ini",
    ],
)

# Python requirements - reference to 3rdparty dependencies
# This will be expanded as we create per-component BUILD files
