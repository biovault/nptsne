#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default, build_shared
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
        docker_entry_script = "./.ci/entry.sh"
    
    print("Version detected", build_shared.get_version())
    
    builder = build_template_default.get_builder(
        docker_entry_script=docker_entry_script
    )
    
    print("Default reference: ", builder.reference)

    builder.remove_build_if(_is_not_shared)
    if platform.system() == "Windows":
        builder.remove_build_if(_is_not_VS15MDonWindows)    
   
    builder.run()
