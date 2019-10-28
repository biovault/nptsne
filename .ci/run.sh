#!/usr/bin/env bash

set -ex

if [[ "$(uname -s)" == 'Darwin' ]]; then
    # if which pyenv > /dev/null; then
    #    eval "$(pyenv init -)"
    # fi
    conda activate conan
fi
   
python build.py
