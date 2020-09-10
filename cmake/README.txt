Building with and without Conan via the ConanSetup.cmake wrapper
================================================================

The release versions of nptsne are built using Conan as package manager. 
Some developers may prefer to work without Conan and do their own package management
manually or using the system package management (if available) or some other package management system.

To facilitate this the Conan & Cmake integration is concentrated in the ConanSetup.cmake file 
along with some addition conan support scripts in the conan sub directory of this cmake folder.

Usage
=====

To use Conan the option: NPTSNE_BUILD_WITH_CONAN is set to ON (the default in the top level CMakeLists.txt)
To use another packaging system the option: NPTSNE_BUILD_WITH_CONAN is set to OFF

Difference from regular conan build
===================================
The package requirements and options that Conan installs are defined in the ConanSetup.cmake rether than in a
separate conanfile.py or conanfile.txt. (see https://github.com/conan-io/cmake-conan for more)

Background
========== 
This system and the ConanSetup.cmake is inspired by the Conan system on https://github.com/ufz/ogs (opengeosys.org)
which (apparently) was inspired from the Conan wrapper example at https://github.com/conan-io/cmake-conan 
There are other projects adopting a similar flexible approach to Conan package management e.g.
https://github.com/caiorss/cpp-project-templates/tree/master/wxwidgets (search on github for conan_cmake_run
to find more examples).

Projects ogs demonstrates more possibilities: e.g. loading version numbers from a json file.
