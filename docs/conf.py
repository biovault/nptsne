# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import sphinx_rtd_theme

# -- Project information -----------------------------------------------------

project = "nptsne"
copyright = "2021, TU Delft, LUMC"
author = "Baldur van Lew"
zenodo_url = "https://doi.org/10.5281/zenodo.5801124"
github_branch = "release/1.3.0"

import os
import sys
import subprocess

# Whether the build is running inside RTD
on_rtd = os.environ.get("READTHEDOCS") == "True"

# Part of API documentation for RTD is embedded in the docstrings of the
# binary shared objects. So the version of nptsne is first installed
# corresponding to the RTD versio being built.
if on_rtd:
    # Manually triggering a RTD build can be done using the following recipe
    # Register this version with RTD
    # curl \
    # -X PATCH \
    # -H "Authorization: Token $RTD_TOKEN" https://readthedocs.org/api/v3/projects/nptsne/versions/v$VERSION/ \
    # -H "Content-Type: application/json" \
    # -d '{"active": true, "hidden": false}'
    # Trigger build
    # curl \
    # -X POST \
    # -H "Authorization: Token $RTD_TOKEN" \
    # -H "Content-Type: application/json" \
    # -d '{"active": true, "hidden": false}' https://readthedocs.org/api/v3/projects/nptsne/versions/v$VERSION/builds/
    # Install a version of nptsne to extract the docstrings
    # READTHEDOCS_VERSION : The RTD name of the version which is being built
    rtd_version = os.environ.get("READTHEDOCS_VERSION")
    print(
        f"In ReadTheDocs - build docing for  rtd_version {rtd_version}",
        flush=True,
    )

    # TBD this is incorrect
    # stable represents a tagged version - will be on PyPi
    # non-stable on test.pypi
    install_version = rtd_version
    if install_version[0] == "v":
        install_version = rtd_version[1:]
    if "rc" not in rtd_version and "a" not in rtd_version and "b" not in rtd_version:
        branch = None
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--force-reinstall",
                    f"nptsne=={install_version}",
                ]
            )
        except subprocess.CalledProcessError:
            branch = "stable"
    else:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--pre",
                "--no-deps",
                f"nptsne=={install_version}",
                "--index-url",
                "https://test.pypi.org/simple",
            ]
        )
else:
    sys.path.insert(0, os.path.abspath(os.path.join("..", "installed")))

import nptsne

__version__ = nptsne.__version__
__branch_name__ = nptsne.__branch_name__

mmp = __version__.split(".")
# The short X.Y version
version = "{}.{}".format(mmp[0], mmp[1])
# The full version, including alpha/beta/rc tags

html_title = __version__


rst_epilog = f"""
.. |version| replace:: {__version__}
.. |HSNEdemo_github_url| replace:: `Basic HSNE demo code <https://github.com/biovault/nptsne/tree/{__branch_name__}/demos/BasicHSNEDemo>`__
.. |EXHSNEdemo_github_url| replace:: `Extended HSNE demo code <https://github.com/biovault/nptsne/tree/{__branch_name__}/demos/ExtendedHSNEDemo>`__
.. |Louvdemo_github_url| replace:: `HSNELouvain demo code <https://github.com/biovault/nptsne/tree/{__branch_name__}/demos/HSNELouvainDemo>`__
.. |TTdemo_github_url| replace:: `TextureTsne demo code <https://github.com/biovault/nptsne/tree/{__branch_name__}/demos/TextureTsne>`__
.. |TTEdemo_github_url| replace:: `TextureTsneExtended demo code <https://github.com/biovault/nptsne/tree/{__branch_name__}/demos/TextureTsneExtended>`__
.. |TNotebook_github_url| replace:: `tSNE Jupyter notebook demo <https://github.com/biovault/nptsne/tree/{__branch_name__}/demos/TSNEJupyterNotebook>`__
.. |doctest_github_url| replace:: `Doctest code <https://github.com/biovault/nptsne/tree/{__branch_name__}/test>`__
.. |zenodo_url| replace:: `(see demos + data) <{zenodo_url}>`__
"""


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
needs_sphinx = "3.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# Prefer numpydoc 1.0.0 to napoleon - it handles complex syntax better in Sphinx 3
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.githubpages",
    "sphinx.ext.extlinks",
    "sphinx.ext.autosectionlabel",
    "numpydoc",
    "sphinx_rtd_theme",
    #    'sphinx.ext.napoleon',
]

numpydoc_show_class_members = False

# Include class docstring and init docstring in the  class doc
autoclass_content = "both"

autodoc_default_options = {
    "members": True,  # All members (for module classes in __all__)
    "undoc-members": True,  # Including those without doc strings
    "inherited-members": False,  # Including inherited members
    "imported-members": False,  # Including imported classes (imports from the extension)
    "show-inheritance": False,  # Don't show base classes
    "member-order": "groupwise",  # Logical groups not alphabetical
    "exclude-members": "__init__",  # __init__ function documented in class header
}

autosummary_imported_members = False
autosummary_generate = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
# 'changelogs/*.rst',
exclude_patterns = ["modules.rst", "*.inc"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "nptsnedoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "nptsne.tex", "nptsne Documentation", "Baldur van Lew", "manual"),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "nptsne", "nptsne Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "nptsne",
        "nptsne Documentation",
        author,
        "nptsne",
        "One line description of project.",
        "Miscellaneous",
    ),
]


# -- Extension configuration -------------------------------------------------
# add specific members to the undoc - we document __init__ in the class header
def skip_members(app, what, name, obj, skip, options):
    exclusions = ("__init__",)
    exclude = name in exclusions
    return skip or exclude


def setup(app):
    app.connect("autodoc-skip-member", skip_members)
