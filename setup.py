import sys
from pathlib import Path

p = Path(".")
sys.path.append(str(p.resolve()))

from setuptools import setup
from tools.cmake_utils import CMakeExtension, CMakeBuild
from tools.version_util import get_version
from pathlib import Path
import tempfile


def update_package_full_version(full_version):
    script_path = Path(__file__).resolve().parent.absolute()
    with open(Path(script_path, "nptsne", "nptsne", "_full_version.txt", "w")) as verfile:
        verfile.write(full_version)


#  This temporary directory is used to collect libs
#  for inclusion in the wheel
templibdir = Path(Path(tempfile.gettempdir()), "cibwlibsdir")
full_version = get_version(Path(__file__).resolve().parent)
update_package_full_version(full_version)

setup(
    version=full_version,
    ext_modules=[
        CMakeExtension("_nptsne", "nptsne", templibdir=str(templibdir))
    ],  # provide the extension name and package_name
    cmdclass=dict(build_ext=CMakeBuild),
)
