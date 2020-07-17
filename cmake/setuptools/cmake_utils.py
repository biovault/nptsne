# From the pybind11 CMake example at https://github.com/pybind/cmake_example
# Wraps cmake for cmake based build projects (handy for pybind11 wrapping cpp)

import os
import platform
import re
import sys
import subprocess

from setuptools import Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir='', exclude_arch=False):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        self.exclude_arch = exclude_arch


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if not ext.exclude_arch: 
                if sys.maxsize > 2**32:
                    cmake_args += ['-A', 'x64']
                build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j3']
        
        # Building with conan
        cmake_args += ['-DNPTSNE_BUILD_WITH_CONAN=ON']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        process = subprocess.run(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        while True:
            output = process.stdout.readline()
            err = process.stderr.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.strip())
            if err:
                print(err.strip())
                
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)