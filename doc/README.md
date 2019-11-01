# Documentation for nptsne

This directory contains the source for the **nptsne** documentation and release notes. Once built the html output should be places in the nptsne master branch under docs to allow it to appear in [the github io page](https://biovault.github.io/nptsne/)

Sphinx doc editing/reviewing:

0. pip install the following:
    * the latest nptsne package (to pickup the internal documentation)
    * the sphinx_rtd_theme
    * sphinx-autobuild
1. Install sphinx-autobuild: `pip install sphinx-autobuild`
2. Set working directory to doc: `cd nptsne/doc`
3. Start sphinx-autobuild with output to the root docs: `sphinx-autobuild ./source ../docs`
4. Observe th sphinx-autobuild output for errors in the rst.
5. Open http://127.0.0.1:8000/ to observe built docs
