#!/usr/bin/env bash
echo Python version:
python --version
echo CMake version
cmake --version
echo conan version
conan --version
echo Prepare conan
conan user
# Use a profile to control the conan install
conan profile remove build_type default



