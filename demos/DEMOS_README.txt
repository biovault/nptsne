Running the nptsne demos
========================
The demos run using the uv Python package and project manager. 
The demo directory includes both a pyproject.toml and a uv.lock file.
By installing uv and syncing the packages in the lock-file you will have a ready-to-run
python environent for the demo scripts. The steps needed to do this are listed below

1. Install uv
--------------
If you don't already have uv on you system install information is at 
https://docs.astral.sh/uv/getting-started/

2. Setup the environment
------------------------
In the directory containg the pyproject.tom and the uv.lock file run

uv sync

This will check tha the lock file matches the project settings and if so installs the exact 
package versions in the uv.lock files that are known to work with the demos.

3. Running the demos
--------------------
uv sync as well as setting up an environment also installs each demo as a python script.
It is thus possible to run a demo as follows

uv run <DemoName> <arguments>

The demo scripts are:

JupyterNotebookDemo:  Run a Jupyter server that can be used to run the
                      NPTSNE_notebooktests.ipynb notebook. This 
                      provides an interactive walk through of the APIs
                      of the TextureTsne and TextureTsneExtended.

SimpleTsne:           Creates a tSNE embedding of the MNIST data set and 
                      displays it along with the KLdivergence graph (when available)

ExtendedTsne:         Runs the t-SNE in blocks of 100 iterations 
                      saving an image at the end of each 100 iterations

HSNELouvainDemo:      The demo shows the Louvain method for community detection
                      applied to a HSNE scale derived from the MNIST data.

BasicHSNEDemo:        Navigate the MNIST dataset using hierarchical SNE (SNE)

ExtendedHSNEDemo:     Explore various dataset using hierarchical SNE (HSNE). 
                      Supports drilling down in the hierarchy with tSNE embeddings
                      as visualization.

DocTest:              Execute and validate the example code in the python strings.
                      These tests can be used as a basic validation for the installed 
                      package and as areference for the API.



Each script has a detailed Readme in the demos/src/nptsnedemos/<ScriptName> subdirectory
