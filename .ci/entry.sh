#!/usr/bin/env bash

# The Linux build running in a docker which comes with a
# pre-set python version which may need to be altered
if [[ `uname` != "Linux" ]]; then
    exit 0
fi

echo Requested python verson is: $CONAN_LINUX_PYTHON
export pyver=`python --version | cut -d " " -f 2`   
echo Installed python verson is: $pyver
if [[ "$pyver" != "$CONAN_LINUX_PYTHON" ]]; then
    echo Installing pyenv version $CONAN_LINUX_PYTHON
    pyenv install $CONAN_LINUX_PYTHON
    pyenv global $CONAN_LINUX_PYTHON 
fi
pip install cmake
pip install six==1.12.0
pip install conan==1.19.3 
pip install scikit-build
pip install conan_package_tools==0.29.3 bincrafters_package_tools==0.21.0    
echo After install python version `python --version`
