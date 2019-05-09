from skbuild import setup  # This line replaces 'from setuptools import setup'
from skbuild.setuptools_wrap import upstream_Distribution
# from setuptools.dist import Distribution

__version__ = '0.1.1'
with open("./src/docs/README.md", "r") as fh:
    long_description = fh.read()

#class BinaryDistribution(upstream_Distribution):
#    """Distribution which always forces a binary package with platform name"""
#    def has_ext_modules(foo):
#       return True
					

setup(
    name='nptsne',
    version=__version__,
	author='Nicola Pezzotti, Julian Thijssen, Baldur van Lew',
	description='The nptsne package is designed to export a number of python classes that wrap tSNE. Reference https://arxiv.org/abs/1805.10817',
	long_description=long_description,
    long_description_content_type="text/markdown",
	# Include pre-compiled extension
	packages=['nptsne'],
    package_data={'nptsne': ['nptsne.cp36-win_amd64.pyd', '*.*', '**/*.*']},
#    distclass=BinaryDistribution,
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: Windows",
    ],

)
