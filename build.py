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
    if platform.system() == "Windows":
        docker_entry_script = None
    else:
        docker_entry_script = "./.ci/entry.sh"    
    builder = build_template_default.get_builder(
        reference="nptsne/1.0.0rc1@lkeb/stable",  # suppress conan using the feature/aaa
        docker_entry_script=docker_entry_script
    )

    builder.remove_build_if(_is_not_shared)
    if platform.system() == "Windows":
        builder.remove_build_if(_is_not_VS15MDonWindows)    
   
    builder.run()
