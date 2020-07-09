#!/usr/bin/env bash

set -ex

# if [[ "$(uname -s)" == 'Darwin' ]]; then
    # OS=MacOSX-x86_64
    # wget -O miniconda.sh https://repo.continuum.io/miniconda/Miniconda${OSX_PYTHON:0:1}-latest-$OS.sh
    # bash miniconda.sh -b -p $HOME/miniconda
    # export PATH="$HOME/miniconda/bin:$PATH"
    # conda config --set always_yes yes --set changeps1 no
    # conda config --add channels conda-forge
    # conda update -q conda
    # conda install -q conda-build
    # conda create -q -n build_env python=$OSX_PYTHON
    # source activate build_env  
    # conda install -c conda-forge conan 
# else
    # pip install six==1.12.0
    # pip install conan==1.24.1      
# fi
pip3 install six==1.12.0
pip3 install conan==1.24.1 
pip3 install scikit-build    
pip3 install conan_package_tools==0.32.2 bincrafters_package_tools==0.26.3
pip3 install cmake
pip3 install cibuildwheel==1.5.2
echo Python version:
python --version 

# Automatic detection of arch, compiler, etc. & create conan data dir.    
conan user
