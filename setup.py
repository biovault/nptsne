import sys
from pathlib import Path

p = Path(".")
sys.path.append(str(p.resolve()))

from setuptools import setup
from tools.cmake_utils import CMakeExtension, CMakeBuild

from pathlib import Path
import tempfile

def get_full_version():
    script_path = Path(__file__).resolve().parent.absolute()
    with open(Path(script_path, "full_version.txt"), "r") as verfile:
        lines = verfile.readlines()
        for line in lines:
            version = line.strip()
            return version

#  This temporary directory is used to collect libs
#  for inclusion in the wheel
templibdir = Path(Path(tempfile.gettempdir()), "cibwlibsdir")
full_version = get_full_version()
print(f"Full version in build: {full_version}")
print("Run setuptools")
setup(
    version=full_version,
    ext_modules=[
        CMakeExtension("_nptsne", "nptsne", templibdir=str(templibdir))
    ],  # provide the extension name and package_name
    cmdclass=dict(build_ext=CMakeBuild),
)
