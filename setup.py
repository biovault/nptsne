from setuptools import setup
from tools.cmake_utils import CMakeExtension, CMakeBuild
from tools.version_util import get_version
from pathlib import Path
import tempfile

#  This temporary directory is used to collect libs
#  for inclusion in the wheel
templibdir = Path(Path(tempfile.gettempdir()), "cibwlibsdir")
# print('cibwlibsdir at: ', templibdir)

setup(
    # Always append the build number for tracking purposes - this fits with PEP427
    version=get_version(Path(__file__).resolve().parent),
    ext_modules=[
        CMakeExtension("_nptsne", "nptsne", templibdir=str(templibdir))
    ],  # provide the extension name and package_name
    cmdclass=dict(build_ext=CMakeBuild),
)
