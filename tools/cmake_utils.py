# From the pybind11 CMake example at https://github.com/pybind/cmake_example
# Wraps cmake for cmake based build projects (handy for pybind11 wrapping cpp)

import json
import os
import copy
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib
import urllib.request
import mypy.stubgen
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
        with open(Path(liboutputdir, "__init__.py").absolute(), "w") as f:
            pass


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
            if sys.maxsize > 2**32:
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

        # Prebuilt HDILib, flann and lz4 are downloaded from artifactory 
        cmake_args += ["-DUSE_ARTIFACTORY_LIBS=ON"]

        env = os.environ.copy()
        #env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(
        #    env.get("CXXFLAGS", ""), self.distribution.get_version()
        #)
        #self.announce("CXXFLAGS: {}".format(self.distribution.get_version()), log.INFO)

        self.announce(f"Path is {os.environ['PATH']}", log.INFO)

        # CMake configure
        print("Çalling cmake configure")
        subprocess.check_call(
            ["cmake", "--log-level=VERBOSE", ext.sourcedir] + cmake_args,  # "--trace-expand",
            cwd=self.build_temp,
            env=env,
        )
        # CMake build
        print("Calling cmake build")
        subprocess.check_call(
            ["cmake", "--build", ".", "--verbose"] + build_args,  # "--trace-expand",
            cwd=self.build_temp,
        )

        # Move the conan dependencies for wheel fix-up
        subprocess.check_call(
            ["cmake", "--build", ".", "--target", "bundle_libs", "--config", cfg],
            cwd=self.build_temp,
        )

        print("Files in output dir: ", os.listdir(liboutputdir))
        print("Files in temp libs dir: ", os.listdir(ext.templibdir))
        print("LD_LIBRARY_PATH: ", os.environ.get("LD_LIBRARY_PATH", ""))

        self._generate_stubs(liboutputdir)

    def _generate_stubs(self, liboutputdir: Path):
        import subprocess, sys
        from pathlib import Path

        subprocess.check_call([
            sys.executable, f"{str(Path(Path(__file__).parent, 'debug_import.py'))}"
        ])
        pkg_dir = Path("src/nptsne")
        
        # 1. pybind11-stubgen for the compiled extension
        #    Import name of the extension module e.g. _nptsne
        ext_module_name = "nptsne.libs._nptsne"
        build_pkg_dir = Path(self.build_lib) / "nptsne"
        
        env = copy.deepcopy(os.environ)
        # if os.environ.get("PYTHONPATH", None):
        #  pypath= ":".join([os.environ.get("PYTHONPATH", None), str(liboutputdir)])
        # else:
        #  pypath = str(liboutputdir)
        # if os.environ.get("PYTHONPATH", None):
        #  pypath= ":".join([os.environ.get("PYTHONPATH", None), str(Path(self.build_lib))])
        # else:
        pypath = str(Path(build_pkg_dir.parent).absolute())
        env["PYTHONPATH"] = pypath

        print(f"Running pybind11_stubgen on {ext_module_name} with {pypath} as PYTHONPATH")

        subprocess.check_call([
            sys.executable, "-m", "pybind11_stubgen",
            ext_module_name,
            "--output-dir", str(build_pkg_dir.parent.absolute())],
            env=env
        )
        # Due to the import of .libs._nptsne in the top level __init__.py
        # a duplication of the _nptsne stub directory can be triggered
        dup_nptsne = Path(build_pkg_dir.absolute(), "_nptsne")
        if dup_nptsne.exists():
          print(f"DEBUG removing spurious stub dir: {dup_nptsne}")
          shutil.rmtree(dup_nptsne)

        # pypath = f"{pypath}:{str(liboutputdir.parent)}:{str(liboutputdir.parent.parent)}"
        # env["PYTHONPATH"] = pypath
        # build_pkg_dir = Path(self.build_lib) / "nptsne"
        # print(f"The build package dir is:  {build_pkg_dir.absolute()}")
        # # 2. stubgen for the pure Python hierarchy
        # print(f"Running stubgen on nptse with {pypath} as PYTHONPATH")
        # init_path = build_pkg_dir / "__init__.py"
        # print(f"DEBUG exists: {init_path.exists()}")
        # print(f"DEBUG size: {init_path.stat().st_size}")
        # print(f"DEBUG contents:\n{init_path.read_text()}")

        # 2. mypy stubgen for pure Python modules
        # Run in-process with build_lib_dir on sys.path
        sys.path.insert(0, str(build_pkg_dir.parent.absolute()))
        try:
            mypy.stubgen.main([
                '--package', 'nptsne.hsne_analysis',
                '--output', str(build_pkg_dir.parent.absolute()),
                '--no-analysis',
                '--include-docstrings',
                '--verbose',
            ])
        except SystemExit as e:
            print(f"DEBUG stubgen SystemExit code: {e.code}")
        except Exception as e:
            print(f"DEBUG stubgen Exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            sys.path.pop(0)
        # subprocess.check_call([
        #     sys.executable, "-c",  "import mypy.stubgen; mypy.stubgen.main(['-p', 'nptsne'])",
        #     "--search-path", "",
        #     "--verbose",
        #     "--package", "nptsne",
        #     "--output", "src_ms",
        #     "--no-analysis", # faster, avoids type inference errors
        #     "--include-docstrings",
        #     ],   
        #     env=env,
        #     cwd=str(build_pkg_dir.parent.absolute())
        # )
        for p in build_pkg_dir.parent.rglob("*.pyi"):
          print(p)

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
