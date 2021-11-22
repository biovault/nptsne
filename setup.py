import sys
from pathlib import Path

p = Path(".")
sys.path.append(str(p.resolve()))

from setuptools import setup
from tools.cmake_utils import CMakeExtension, CMakeBuild
from tools.version_util import get_version
from pathlib import Path
import tempfile

# print("starting setup")
#  This temporary directory is used to collect libs
#  for inclusion in the wheel
templibdir = Path(Path(tempfile.gettempdir()), "cibwlibsdir")
# print('cibwlibsdir at: ', templibdir)
# print(f"****Derived version: {get_version(Path(__file__).resolve().parent)}")
vertxt = get_version(Path(__file__).resolve().parent)
script_path = Path(__file__).absolute()
with open(Path(script_path, "nptsne", "_version.txt", "w")) as verfile:
    verfile.write(vertxt)

setup(
    # Always append the build number for tracking purposes - this fits with PEP427
    version=vertxt,
    ext_modules=[
        CMakeExtension("_nptsne", "nptsne", templibdir=str(templibdir))
    ],  # provide the extension name and package_name
    cmdclass=dict(build_ext=CMakeBuild),
)
