# Building and publishing documentation for nptsne

This directory contains the source for the **nptsne** documentation and release notes. Once built the html output should be places in the nptsne master branch under docs to allow it to appear in [the github io page](https://biovault.github.io/nptsne/)

Sphinx doc editing/reviewing:

0. pip install the following:
    * the latest nptsne package (to pickup the internal documentation)
    * sphinx (at time of writing sphinx 1.8.5)
    * the sphinx_rtd_theme
    * sphinx-autobuild
1. Install sphinx-autobuild: `pip install sphinx-autobuild`
2. Set working directory to doc: `cd nptsne/doc`
3. Start sphinx-autobuild with output to the root docs: `sphinx-autobuild ./source ../docs`
4. Observe the sphinx-autobuild output for errors in the rst.
5. Open http://127.0.0.1:8000/ to observe built docs
6. Commit and push doc and docs. The latter will be displayed on [the github io page](https://biovault.github.io/nptsne/)

### Why not ReadTheDocs?

The interface documentation for nptsne is found in the docstrings
in the pybind11 cpp binding. This was done in order to ensure that
it would be kept up to data with modifications of the ntpsne classes and their APIs.

Sphinx loads the nptsne module, extracts and processes the formatted doc strings. Unfortunately on ReadTheDocs it is not possible to install the extra libraries needed to load the nptsne module.

For this reason the source of the docs is in ./doc and the output in ./docs which will appear on the [the github io page](https://biovault.github.io/nptsne/)
