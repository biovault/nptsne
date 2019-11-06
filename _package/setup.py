from skbuild import setup  # This line replaces 'from setuptools import setup'
from skbuild.setuptools_wrap import upstream_Distribution
from setuptools import find_packages
import sys
import os

with open(os.path.join(os.path.dirname(__file__), "nptsne", "_version.txt")) as fp:
    __version__ = fp.read().strip()
# from setuptools.dist import Distribution

with open("./docs/README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='nptsne',
    version=__version__,
	author='Nicola Pezzotti, Thomas Höllt, Julian Thijssen, Baldur van Lew',
    author_email='b.van_lew@lumc.nl',
	description='The nptsne package is designed to export a number of python classes that wrap tSNE. Reference https://arxiv.org/abs/1805.10817v2',
	long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='tSNE embedding GPU',
    url='https://biovault.github.io/nptsne',
    project_urls={
        "Bug Tracker": "https://github.com/biovault/nptsne/issues",
        "Documentation": "https://biovault.github.io/nptsne",
        "Source Code": "https://github.com/biovault/nptsne"
    },
    include_package_data=True,
	packages=find_packages(),
# 	TODO add test_require for the behave tests see https://stackoverflow.com/questions/21698004/python-behave-integration-in-setuptools-setup-py
	classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: C++"
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy>=1.11.0'
    ]

)
