#!/usr/bin/env bash

set -ex

if [[ "$(uname -s)" == 'Darwin' ]]; then
    brew update || brew update
    brew outdated pyenv || brew upgrade pyenv
    brew install pyenv-virtualenv
    brew install cmake || brew upgrade cmake || true

    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    curl -I -L homebrew.bintray.com || true
    pyenv install 3.7.1
    pyenv virtualenv -p python3.7 3.7.1 conan
    curl -I -L homebrew.bintray.com || true
    pyenv rehash
    curl -I -L homebrew.bintray.com || true 
    pyenv activate conan
    curl -I -L homebrew.bintray.com || true
    pyenv deactivate
    curl -I -L homebrew.bintray.com || true 
    pyenv activate conan
    curl -I -L homebrew.bintray.com || true   
fi

pip install conan --upgrade
pip install conan_package_tools bincrafters_package_tools

# Automatic detection of arch, compiler, etc. & create conan data dir.    
conan user
