import sys
from pathlib import Path

p = Path(".")
sys.path.append(str(p.resolve()))

from setuptools import setup
from tools.cmake_utils import CMakeExtension, CMakeBuild
from tools.version_util import get_version, get_branch_name
from pathlib import Path
import tempfile


def update_package_full_version(full_version):
    script_path = Path(__file__).resolve().parent.absolute()
    with open(Path(script_path, "src", "nptsne", "_full_version.txt"), "w") as verfile:
        verfile.write(full_version)


def update_package_branch_name(branch_name):
    script_path = Path(__file__).resolve().parent.absolute()
    with open(Path(script_path, "src", "nptsne", "_branch_name.txt"), "w") as brnchfile:
        brnchfile.write(branch_name)


#  This temporary directory is used to collect libs
#  for inclusion in the wheel
templibdir = Path(Path(tempfile.gettempdir()), "cibwlibsdir")
full_version = get_version(Path(__file__).resolve().parent)
update_package_full_version(full_version)
branch_name = get_branch_name(Path(__file__).resolve().parent)
update_package_branch_name(branch_name)

setup(
    version=full_version,
    ext_modules=[
        CMakeExtension("_nptsne", "nptsne", templibdir=str(templibdir))
    ],  # provide the extension name and package_name
    cmdclass=dict(build_ext=CMakeBuild),
)
