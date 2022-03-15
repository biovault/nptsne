# From the pybind11 CMake example at https://github.com/pybind/cmake_example
# Wraps cmake for cmake based build projects (handy for pybind11 wrapping cpp)

import json
import os
import pathlib
import platform
import re
import subprocess
import sys
import time
import urllib
import urllib.request
from setuptools import Extension
from setuptools.command.build_ext import build_ext
from distutils import log
from distutils.version import LooseVersion
from pathlib import Path


class CMakeExtension(Extension):
    def __init__(self, name, package_name, sourcedir="", templibdir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        self.package_name = package_name
        # self.templibdir = tempfile.mkdtemp()
        self.templibdir = templibdir
        # print('Temp lib dir is :', self.templibdir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: "
                + ", ".join(e.name for e in self.extensions)
            )

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r"version\s*([\d.]+)", out.decode()).group(1))
            if cmake_version < "3.1.0":
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            if ext.templibdir:
                # create the tempdir if it is not yet available
                tempdir = Path(ext.templibdir)
                tempdir.mkdir(exist_ok=True)
            self.build_extension(ext)

    def build_extension(self, ext):
        self.announce("Building for package: {}".format(ext.package_name), log.INFO)
        self.announce("Building extension: {}".format(ext.name), log.INFO)

        build_temp = pathlib.Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)
        extdir = pathlib.Path(self.get_ext_fullpath(ext.name)).parent.absolute()
        extdir.mkdir(parents=True, exist_ok=True)
        #  I prefer to place the libraries in a "libs" subdir in the package
        liboutputdir = extdir.joinpath(ext.package_name, "libs")
        liboutputdir.mkdir(parents=True, exist_ok=True)

        cmake_args = [
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={}".format(liboutputdir),
            "-DPYTHON_EXECUTABLE={}".format(sys.executable),
        ]

        cfg = "Debug" if self.debug else "Release"
        self.announce("CMake configuration: {}".format(cfg), log.INFO)
        build_args = ["--config", cfg]

        # Also limit Windows to single config build -
        # Causes Conan to load a single set of libs
        cmake_args += ["-DCMAKE_BUILD_TYPE=" + cfg, "-DTEMP_LIBS_DIR=" + ext.templibdir]
        if platform.system() == "Windows":
            # VS can produce separate RELEASE or DEBUG outputs
            cmake_args += [
                "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}".format(cfg.upper(), liboutputdir)
            ]
            if sys.maxsize > 2 ** 32:
                cmake_args += ["-A", "x64"]
            build_args += ["--", "/m"]
            # If vcvarsall.bat has been run use that setting
            if os.environ.get("VisualStudioVersion", None) is not None:
                if os.environ["VisualStudioVersion"] == "15.0":
                    cmake_args += ["-G", "Visual Studio 15 2017"]
                elif os.environ["VisualStudioVersion"] == "16.0":
                    cmake_args += ["-G", "Visual Studio 16 2019"]
        elif platform.system() == "Linux":
            build_args += ["--", "-j3"]
            cmake_args += ["-DLIBCXX=libstdc++"]
        elif platform.system() == "Darwin":
            # Xcode automatically optimizes core usage
            # as default Xcode will create a release subdir
            cmake_args += [
                "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}".format(cfg.upper(), liboutputdir)
            ]
            build_args += ["--"]
        else:
            raise RuntimeError("Unsupported platform")

        # Building with conan - conan is used to install the dependencies
        cmake_args += ["-DNPTSNE_BUILD_WITH_CONAN=ON"]

        env = os.environ.copy()
        env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get("CXXFLAGS", ""), self.distribution.get_version()
        )
        self.announce("CXXFLAGS: {}".format(self.distribution.get_version()), log.INFO)

        # Set the conan profile in this context now that the compiler is set
        # in many_linux2010 the settings are:
        """
            os=Linux
            os_build=Linux
            arch=x86_64
            arch_build=x86_64
            compiler=gcc
            compiler.version=8
            compiler.libcxx=libstdc++
        """

        self.announce(f"Path is {os.environ['PATH']}", log.INFO)
        self.announce("Set the conan build profile from the current context", log.INFO)
        subprocess.run(
            ["conan", "--version"],
            cwd=self.build_temp,
        )
        subprocess.check_call(
            ["conan", "profile", "new", "default", "--detect", "--force"], cwd=self.build_temp
        )
        self.announce("Show conan home dir", log.INFO)
        subprocess.check_call(
            ["conan", "config", "home"],
            cwd=self.build_temp,
        )
        self.announce("Show conan remotes", log.INFO)
        subprocess.check_call(
            ["conan", "remote", "list"],
            cwd=self.build_temp,
        )
        subprocess.check_call(["conan", "profile", "show", "default"], cwd=self.build_temp)

        if platform.system() == "Windows":
            self.announce("Remove build_type from conan profile on windows", log.INFO)
            subprocess.check_call(
                ["conan", "profile", "remove", "settings.build_type", "default"],
                cwd=self.build_temp,
            )
            subprocess.check_call(["conan", "profile", "show", "default"], cwd=self.build_temp)

        # CMake configure
        subprocess.check_call(["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        # CMake build
        subprocess.check_call(
            ["cmake", "--build", ".", "--verbose"] + build_args, cwd=self.build_temp
        )

        # get the dependent libs (were supplied by Conan)
        # os.environ['LD_LIBRARY_PATH'] = liboutputdir

        # Move the conan dependencies for wheel fix-up
        subprocess.check_call(
            ["cmake", "--build", ".", "--target", "bundle_libs", "--config", cfg],
            cwd=self.build_temp,
        )

        print("Files in output dir: ", os.listdir(liboutputdir))
        print("Files in temp libs dir: ", os.listdir(ext.templibdir))
        print("LD_LIBRARY_PATH: ", os.environ.get("LD_LIBRARY_PATH", ""))


def versions(package_name, testpypi=False):
    url = "https://test.pypi.org/pypi/{}/json".format(
        package_name,
    )
    if testpypi:
        url = "https://test.pypi.org/pypi/{}/json".format(
            package_name,
        )
    data = json.load(urllib.request.urlopen(url))
    versions = list(data["releases"].keys())
    return versions


def search_for_version(version, number_of_waits, testpypi=False):
    wait_delay = 2
    for i in range(number_of_waits):
        if version in versions("nptsne", testpypi):
            print("Found")
            exit(0)
            break
        wait_delay = 2 * wait_delay
        time.sleep(wait_delay)
    print("Not found")
    exit(1)
