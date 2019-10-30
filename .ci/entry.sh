#!/usr/bin/env bash

# The Linux build running in a docker which comes with a
# pre-set python vershion which may need to be altered
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
pip install conan 
pip install scikit-build
pip install conan_package_tools bincrafters_package_tools    
echo After install python version `python --version`
