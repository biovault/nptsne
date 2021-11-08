# -*- coding: utf-8 -*-

from conans import ConanFile, tools
from conan.tools.cmake import CMakeDeps, CMake, CMakeToolchain
import os
import sys
from pathlib import Path

# Python version for wheel building
with open(os.path.join(os.path.dirname(__file__), "version.txt")) as fp:
    __version__ = fp.read().strip()

__py_version__ = "{}.{}".format(sys.version_info.major, sys.version_info.minor)
__py_tag__ = "cp{}{}".format(sys.version_info.major, sys.version_info.minor)


class NptsneConan(ConanFile):
    name = "nptsne"
    version = __version__
    description = (
        "nptsne is a numpy compatible python binary package"
        " that offers a number of APIs for fast tSNE calculation."
    )
    topics = ("python", "analysis", "n-dimensional", "tSNE")
    url = "https://github.com/biovault/nptsne"

    author = "B. van Lew <b.van_lew@lumc.nl>"  # conanfile author
    license = "MIT"  # License use SPDX Identifiers https://spdx.org/licenses/
    exports = ["LICENSE.md", "version.txt"]  # Packages the license for the conanfile.py
    generators = "CMakeDeps"
    default_user = "lkeb"
    default_channel = "stable"

    # Options may need to change depending on the packaged library
    settings = {"os": None, "build_type": None, "compiler": None, "arch": None}
    options = {"shared": [True, False], "fPIC": [True, False], "python_version": "ANY"}
    default_options = {"shared": True, "fPIC": True, "python_version": __py_version__}
    exports_sources = "*"

    _source_subfolder = name
    requires = "HDILib/1.2.4@lkeb/testing"

    def system_requirements(self):
        if tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                installer.install("liblz4-dev")
            # Centos like: -See prepare_build_linux.sh
        # Move to batch file for more control over brew
        # if tools.os_info.is_macos:
        #    installer = tools.SystemPackageTool()
        #    installer.install('libomp')
        #    installer.install('lz4')

    def generate(self):
        generator = None
        if self.settings.os == "Macos":
            generator = "Xcode"

        tc = CMakeToolchain(self, generator=generator)
        if self.settings.os == "Windows" and self.options.shared:
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["BUILD_PYTHON_VERSION"] = __py_version__
        tc.variables["PYBIND11_PYTHON_VERSION"] = __py_version__
        tc.variables["CMAKE_INSTALL_PREFIX"] = Path(self.package_folder).as_posix()
        # if tools.os_info.is_linux:
        #    tc.variables["LIBCXX"] = "libstdc++"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def configure(self):
        # self.options["HDILib"].shared = False
        if tools.os_info.is_linux:
            self.settings.compiler.libcxx = "libstdc++"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def package_id(self):
        self.info.options.python_version = "{}.{}".format(
            sys.version_info.major, sys.version_info.minor
        )

    def build(self):
        # 1.) build the python extension
        # and
        # 2.) install the python binary extension and dependencies
        # into a dist directory under _package
        cmake = CMake(self)
        cmake.configure()
        cmake.install(build_type="Release")
        # 3.) set the platform name
        plat_names = {
            "Windows": "win_amd64",
            "Linux": "linux_x86_64",
            "Macos": "macosx-10.6-intel",
        }
        if self.settings.os == "Macos" or self.settings.os == "Linux":
            self.run("ls -l", cwd=os.path.join(self.package_folder, "_package"))
        # 4.) Make the python wheel from the _package using python setup.py
        self.run(
            "python setup.py bdist_wheel "
            "--plat-name={0} --dist-dir={1} --python-tag={2}".format(
                plat_names[str(self.settings.os)],
                os.path.join(self.package_folder, "dist"),
                __py_tag__,
            ),
            cwd=os.path.join(self.package_folder, "_package"),
        )

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        self.copy("*.h", dst="include", keep_path=True)
        self.copy("*.hpp", dst="include", keep_path=True)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.whl", dst="dist", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
