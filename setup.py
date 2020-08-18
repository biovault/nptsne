from setuptools import setup
from cmake_utils import CMakeExtension, CMakeBuild
import tempfile
import os

templibdir = os.environ.get('LIBSDIR', '/tmp/cibwlibsdir')
print("GIT_DERIVED_BUILD_NUMBER = {}".format(os.environ.get('GIT_DERIVED_BUILD_NUMBER', 'not found')) 
setup(
    ext_modules=[CMakeExtension('_nptsne', 'nptsne', templibdir=templibdir)],  # provide the extension name and package_name
    cmdclass=dict(build_ext=CMakeBuild),
)
