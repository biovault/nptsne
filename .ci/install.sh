#!/usr/bin/env bash

set -ex

pip3 install six==1.12.0
pip3 install conan==1.24.1 
pip3 install scikit-build    
pip3 install conan_package_tools==0.32.2 bincrafters_package_tools==0.26.3
pip3 install cmake
echo Python version:
python --version 

