#!/usr/bin/env bash
set -x 
echo ** Start build environment preparation 
yum remove -y cmake 
yum install -y lz4-devel libXrandr-devel libXinerama-devel libXcursor-devel libXi-devel
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
which python
echo Python version:
python --version
echo CMake version
cmake --version 
echo conan version
conan --version 
echo Prepare conan
conan user 
cat $1/cert.pem >> ~/.conan/cacert.pem 
conan remote add -f lkeb-artifactory https://lkeb-artifactory.lumc.nl/artifactory/api/conan/conan-local