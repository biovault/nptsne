from setuptools import setup
from cmake_utils import CMakeExtension, CMakeBuild

setup(
    ext_modules=[CMakeExtension('_nptsne', 'nptsne')],  # provide the extension name and package_name
    cmdclass=dict(build_ext=CMakeBuild),
)
