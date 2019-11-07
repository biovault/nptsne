#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default, build_shared
from conans import tools
import os
import platform
from cpt.ci_manager import CIManager
from cpt.printer import Printer

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
        
    printer = Printer(None)
    ci_manager = CIManager(printer)
    branch = ci_manager.get_branch()
    version = build_shared.get_version()
    recipe = build_shared.get_recipe_path(None)
    name = build_shared.get_name_from_recipe(recipe=recipe)
    username, version, kwargs = build_shared.get_conan_vars(recipe=recipe)
    print("Branch detected: ", branch)
    print("Version detected: ", build_shared.get_version())
    
    tools.environment_append({"CONAN_SOURCE_BRANCH": branch})

    new_reference = None
    # for builds other than release create a separate channel
    if not branch.startswith("release"):
        new_reference = "{}/{}@{}/{}".format(name, version, username, branch.replace('/', '_'))
        print("Generated reference: ", new_reference)
    
    builder = build_template_default.get_builder(
        docker_entry_script=docker_entry_script,
        reference=new_reference
    )
    
    print("Default reference: ", builder.reference)

    builder.remove_build_if(_is_not_shared)
    if platform.system() == "Windows":
        builder.remove_build_if(_is_not_VS15MDonWindows)    
   
    builder.run()
