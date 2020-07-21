# From the pybind11 CMake example at https://github.com/pybind/cmake_example
# Wraps cmake for cmake based build projects (handy for pybind11 wrapping cpp)

import logging
import os
import pathlib
import platform
import re
import sys
import subprocess

from distutils.version import LooseVersion
from setuptools import Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

def log_subprocess_output(out_bytes):
    print(out_bytes.decode('utf-8'))


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: " +
                ", ".join(
                    e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(
                re.search(
                    r'version\s*([\d.]+)',
                    out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        print("CMake configuration ", cfg)
        build_args = ['--config', cfg]

        # Also limit Windows to single config build - building both Release &
        # Debug together fails
        cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
        if platform.system() == "Windows":
            #VS places output libs in Release or Debug subdir
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            build_args += ['--', '-j3']

        # Building with conan
        cmake_args += ['-DNPTSNE_BUILD_WITH_CONAN=ON']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''), self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        out = subprocess.check_output(['cmake', ext.sourcedir] +
                              cmake_args, cwd=self.build_temp, env=env)
        log_subprocess_output(out)


        out = subprocess.check_output(['cmake', '--build', '.', '--verbose'] +
                              build_args, cwd=self.build_temp)
        log_subprocess_output(out)
        
