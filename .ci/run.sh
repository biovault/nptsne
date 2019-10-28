#!/usr/bin/env bash

set -ex

if [[ "$(uname -s)" == 'Darwin' ]]; then
    # if which pyenv > /dev/null; then
    #    eval "$(pyenv init -)"
    # fi
    source activate build_env
fi
   
python build.py
