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
        docker_entry_script = """pyver=$(python --version | cut -d " " -f 2); echo "Current py ver is : $pyver"
echo Requested python verson is: $CONAN_LINUX_PYTHON
echo Current py version is: $pyver
if [ "$pyver" != "$CONAN_LINUX_PYTHON" ]; then
    pyenv install $CONAN_LINUX_PYTHON
    pyenv global $CONAN_LINUX_PYTHON 
    pip install cmake
    pip install conan 
fi
pip install scikit-build
pip install conan_package_tools bincrafters_package_tools    
echo python version `python --version`
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
