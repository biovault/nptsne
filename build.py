#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default
import os
import platform

def _is_not_shared(build):
    return not(build.options['nptsne:shared'] == True)
    
def _is_not_VS15MDonWindows(build):
    return not (
        build.settings["compiler.version"] == '15' and
        build.settings["compiler.runtime"] == 'MD') 
    
if __name__ == "__main__":

    docker_entry_script = None
    if platform.system() == "Linux":
        docker_entry_script = """wget -O miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sudo bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
conda config --set always_yes yes --set changeps1 no
conda config --add channels conda-forge
conda update -q conda
conda install -q conda-build
echo Creating conda env for python version $CONAN_LINUX_PYTHON
conda create -q -n build_env python=$CONAN_LINUX_PYTHON
source activate build_env  
conda install -n build_env cmake
conda install -c conda-forge conan 
conda install -c conda-forge scikit-build
pip install conan_package_tools bincrafters_package_tools
echo Conda python version `python --version`
echo run_create_in_docker at `which run_create_in_docker`
ls -al `which run_create_in_docker`
run_create_in_docker
echo Run create finished
alias run_create_in_docker='echo Done'"""
        
    builder = build_template_default.get_builder(
        reference="nptsne/1.0.0rc1@lkeb/stable",  # suppress conan using the feature/aaa
        docker_entry_script=docker_entry_script
    )

    builder.remove_build_if(_is_not_shared)
    if platform.system() == "Windows":
        builder.remove_build_if(_is_not_VS15MDonWindows)    
   
    builder.run()
