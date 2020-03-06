# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import sys
import json

# Python version for wheel building
with open(os.path.join(os.path.dirname(__file__), "version.txt")) as fp:
    __version__ = fp.read().strip()

__py_version__ = "{}.{}".format(sys.version_info.major, sys.version_info.minor) 
__py_tag__ = "cp{}{}".format(sys.version_info.major, sys.version_info.minor)
 
   
class NptsneConan(ConanFile):
    name = "nptsne"
    # branch = "release/1.0.0"
    version = __version__
    description = "nptsne is a numpy compatible python binary package that offers a number of APIs for fast tSNE calculation."
    topics = ("python", "analysis", "n-dimensional", "tSNE")
    url = "https://github.com/biovault/nptsne"

    author = "B. van Lew <b.van_lew@lumc.nl>" #conanfile author
    license = "MIT"  # License for packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports = ["LICENSE.md", "version.txt"]      # Packages the license for the conanfile.py
    generators = "cmake"
    default_user = "lkeb"
    default_channel = "stable"

    # Options may need to change depending on the packaged library
    settings = {"os": None, "build_type": None, "compiler": None, "arch": None}
    options = {"shared": [True, False], "fPIC": [True, False], "python_version": "ANY"}
    default_options = {"shared": True, "fPIC": True, "python_version": __py_version__}
    exports_sources = "*"

    _source_subfolder = name
    # For now use conan and bincrafters - we may wish to host our own versions
    requires = (
        "pybind11/2.2.4@conan/stable",
        "HDILib/latest@biovault/stable"
    )   
    
    def system_requirements(self):
        if tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                installer.install('liblz4-dev')
        if tools.os_info.is_macos:           
            installer = tools.SystemPackageTool()  
            installer.install('lz4')

    def requirements(self):
        if tools.os_info.is_windows:
            self.requires.add("glfw/3.3@bincrafters/stable")
            
    def system_requirements(self):
        if tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                installer.install('liblz4-dev')
                installer.install('libglfw3')
                installer.install('libglfw3-dev')
        if tools.os_info.is_macos:           
            installer = tools.SystemPackageTool()  
            installer.install('lz4')
            installer.install('glfw')
            
    def configure(self):
        self.options["HDILib"].shared = False
        
    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC 
    
    def package_id(self):
        self.info.options.python_version = "{}.{}".format(sys.version_info.major, sys.version_info.minor) 
        
    # def source(self):
        # source_url = self.url
        # self.run("git clone {0}.git".format(self.url))
        # os.chdir("./{0}".format(self._source_subfolder))
        # branch = os.getenv("CONAN_SOURCE_BRANCH", "master")
        # print("Checking out branch: ", branch)
        # self.run("git checkout {0}".format(branch))
        # os.chdir("..")

    def _configure_cmake(self):
        if self.settings.os == "Macos":
            cmake = CMake(self, generator='Xcode')
        else:
            cmake = CMake(self)
        if self.settings.os == "Windows" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        cmake.definitions["BUILD_PYTHON_VERSION"] = __py_version__  
        cmake.definitions["PYBIND11_PYTHON_VERSION"] = __py_version__  
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = os.path.join(self.package_folder)
        cmake.configure()
        cmake.verbose = True
        return cmake

    def build(self):
        # print("This conanfile should be invoked from python setup via cmake")
        # print("e.g. >python setup.py bdist_wheel")
        # pass
        cmake = self._configure_cmake()
        cmake.build()
        cmake.install()
        # set the platform name 
        plat_names = {'Windows': 'win_amd64', 'Linux': 'linux_x86_64', "Macos": 'macosx-10.6-intel'}
        if self.settings.os == "Macos" or self.settings.os == "Linux":
            self.run('ls -l', cwd=os.path.join(self.package_folder, "_package"))
        self.run('python setup.py bdist_wheel --plat-name={0} --dist-dir={1} --python-tag={2}'.format(
            plat_names[str(self.settings.os)], 
            os.path.join(self.package_folder, 'dist'),
            __py_tag__
        ), cwd=os.path.join(self.package_folder, "_package"))

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
        
