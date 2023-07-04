[![Build Status](https://github.com/biovault/nptsne/actions/workflows/wheels.yml/badge.svg?release/1.3.0)](https://github.com/biovault/nptsne/tree/release/1.3.0)

[![Documentation Status](https://readthedocs.org/projects/nptsne/badge/?version=stable)](https://nptsne.readthedocs.io/en/v1.3.0/)

# nptsne

**nptsne** is a numpy compatible python binary package that offers a number of APIs for fast tSNE calculation and HSNE modelling.

For more detail see the [documentation for the current release - 1.3.0](https://nptsne.readthedocs.io/en/v1.3.0/)

Currently python 3.6, 3.7, and 3.8 are supported on Windows, Mac and Linux using [cibuildwheel](https://cibuildwheel.readthedocs.io/en/stable/)

## Demo software using nptsne

Can be downloaded from [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5801124.svg)](https://doi.org/10.5281/zenodo.5801124)

## Building

The *requirements.txt* and the *pyproject.toml* contain the list of build requirements.

- Add the biovault conan remote (for prebuilt packages):
```
conan remote add conan-biovault https://lkeb-artifactory.lumc.nl/artifactory/api/conan/conan-local
```

- Run the build using cibuildwheel for a platform choose one of windows or macos or linux.

```
python -m cibuildwheel --output-dir wheelhouse --platform <windows|macos|linux>
```

The *build* line in *pyproject.toml* can be modified to change which versions (3.6, 3.7 etc) of the wheels are built.

The project is built using python *setuptools*. At time of the  current release *setup.cfg* is still required for package *metadata* and *options*.  In future versions it may be possible to migrate fully to *pyproject.toml*.
### Development build & install using python

On Windows if multiple versions of Visual Studio are present the x64 Native Tools batch
(vcvarsall.bat) can be run first to select the correct version. At the moment only
VS 2017 (version 15.0) is supported.

```shell
pip install -v -e .
````

This will automatically create a *build* subdirectory build the bindings and create an .egg-link file in the current python environment.

On Windows a *_nptsne.sln* file will be present under the build directory

Builds are performed "in tree" (see the *pyproject.toml PIP_USE_FEATURE entry)

### Development debug builds

TBD
