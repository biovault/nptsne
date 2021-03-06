[![Build Status](https://travis-ci.com/biovault/nptsne.svg?branch=master)](https://travis-ci.com/biovault/nptsne)

[![Build status](https://ci.appveyor.com/api/projects/status/w2paw56r8mju1k2h/branch/master?svg=true)](https://ci.appveyor.com/project/bldrvnlw/nptsne/branch/master)


[![Documentation Status](https://readthedocs.org/projects/nptsne/badge/?version=stable)](https://nptsne.readthedocs.io/en/release-1.1.0/)

# nptsne

**nptsne** is a numpy compatible python binary package that offers a number of APIs for fast tSNE calculation and HSNE modelling.

For more detail see the [documentation for the current release - 1.1.0](https://nptsne.readthedocs.io/en/release-1.1.0)

Currently python 3.6, 3.7, and 3.8 are supported on Windows, Mac and Linux using [cibuildwheel](https://cibuildwheel.readthedocs.io/en/stable/)

## Demo software using nptsne

Can be downloaded from [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4275752.svg)](https://doi.org/10.5281/zenodo.4275752)

## Building

The *requirements.txt* and the *pyproject.toml* contain the list of build requirements.

- Add the biovault conan remote (for prebuilt packages):
```
conan remote add conan-biovault http://cytosplore.lumc.nl:8081/artifactory/api/conan/conan-local
```

#### Development build & install using python
```shell
pip install -v -e .
````

This will automatically create a *build* subdirectory build the bindings and create an .egg-link file in the current python environment.

On Windows a *_nptsne.sln* file will be present under the build directory

#### Alternative manual Windows build

 - Make a build directory below the HDILib project root.
    For example: *./_build_release* or *./_build_debug*
    (<u>when using conan the source directories are shared but
    separate build directories should be used for release and debug.</u>)
 - In the python environment (with conan and cmake accessible)
 cd to the build directory and issue the following (for VisualStudio 2017):
```
cmake .. -G "Visual Studio 15 2017 Win64" -DCMAKE_BUILD_TYPE=Release -DNPTSNE_BUILD_WITH_CONAN=ON
```      
    (*Note: this assumes that the build dir is one level down from the project root.
    The default of NPTSNE_BUILD_WITH_CONAN is OFF*)
 - If all goes well Conan will have installed the dependencies in its cache and
 created the required defines for the Cmake configuration.
 Open the .sln in VisualStudio and build ALL_BUILD for Release or Debug matching the CMAKE_BUILD_TYPE.
     On Windows the result of the build are three *.lib files
