# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import json


class NptsneConan(ConanFile):
    name = "nptsne"
    version = "1.0.0rc1"
    description = "nptsne is a numpy compatible python binary package that offers a number of APIs for fast tSNE calculation."
    topics = ("python", "analysis", "n-dimensional", "tSNE")
    url = "https://github.com/biovault/nptsne"
    branch = "feature/conan-build"
    author = "B. van Lew <b.van_lew@lumc.nl>" #conanfile author
    license = "MIT"  # License for packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports = ["LICENSE.md"]      # Packages the license for the conanfile.py
    generators = "cmake"

    # Options may need to change depending on the packaged library
    settings = {"os": None, "build_type": None, "compiler": None, "arch": None}
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    export_sources = "CMakeLists.txt", "hdi/*"

    _source_subfolder = name
    # For now use conan and bincrafters - we may wish to host our own versions
    requires = (
        "pybind11/2.2.4@conan/stable",
        "glfw/3.3@bincrafters/stable",
        "HDILib/1.0.0-alpha1@lkeb/stable"
    )   
    

    def system_requirements(self):
        if tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                installer.install('liblz4-dev')
        if tools.os_info.is_macos:           
            installer = tools.SystemPackageTool()  
            installer.install('lz4')

    def system_requirements(self):
        if tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                installer.install('liblz4-dev')
        if tools.os_info.is_macos:           
            installer = tools.SystemPackageTool()  
            installer.install('lz4')
            
    def configure(self):
        self.options["HDILib"].shared = False
        
    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC 
    
    def source(self):
        source_url = self.url
        self.run("git clone {0}.git".format(self.url))
        os.chdir("./{0}".format(self._source_subfolder))
        self.run("git checkout {0}".format(self.branch))
        os.chdir("..")

    def _configure_cmake(self):
        if self.settings.os == "Macos":
            cmake = CMake(self, generator='Xcode')
        else:
            cmake = CMake(self)
        if self.settings.os == "Windows" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        cmake.definitions["BUILD_PYTHON_VERSION"] = "3.7"  
        cmake.configure(source_folder=self._source_subfolder)
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
        self.run('python setup.py bdist_wheel --plat-name={0} --dist-dir={1}'.format(
            plat_names[str(self.settings.os)], 
            os.path.join(self.build_folder, 'dist')
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


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
