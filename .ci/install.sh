#!/usr/bin/env bash

set -ex

if [[ "$(uname -s)" == 'Darwin' ]]; then
    OS=MacOSX-x86_64
    wget -O miniconda.sh https://repo.continuum.io/miniconda/Miniconda${OSX_PYTHON:0:1}-latest-$OS.sh
    bash miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    conda config --set always_yes yes --set changeps1 no
    conda config --add channels conda-forge
    conda update -q conda
    conda install -q conda-build
    conda create -q -n build_env python=$OSX_PYTHON
    source activate build_env  
    conda install -n build_env cmake
    conda install -c conda-forge conan 
    conda install -c conda-forge scikit-build
else
    pip install conan --upgrade
    pip install scikit-build         
fi

pip install conan_package_tools bincrafters_package_tools


# Automatic detection of arch, compiler, etc. & create conan data dir.    
conan user
