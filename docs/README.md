# Build the documentation

Install the documentation dependencies into the current environment and build HTML:

```bash
python -m pip install -e ".[docs]"
python docs/make.py html
```

To remove generated output:

```bash
python docs/make.py clean
```

The build helper resolves the `docs/` source and `docs/_build/` output paths from its own location, so it can be invoked from any working directory. All Sphinx builds treat warnings as errors.
