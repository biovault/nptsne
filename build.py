#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default, build_shared
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
    default_reference = ci_manager.reference
    print("Branch detected: ", branch)
    print("Version detected: ", build_shared.get_version())
    print("Default reference: ", default_reference)
    
    refstart,refend = default_reference.split('@')
    name, _ = refstart.split('/')
    new_reference = None
    # for builds other than release merge the branchname into the reference
    if not branch.startswith("release"):
        new_reference = "{}/{}_{}@".format(name, version, branch.replace('/', '_'), refend)
        print("Modified reference: ", new_reference)
    
    builder = build_template_default.get_builder(
        docker_entry_script=docker_entry_script,
        reference=new_reference
    )
    
    print("Default reference: ", builder.reference)

    builder.remove_build_if(_is_not_shared)
    if platform.system() == "Windows":
        builder.remove_build_if(_is_not_VS15MDonWindows)    
   
    builder.run()
