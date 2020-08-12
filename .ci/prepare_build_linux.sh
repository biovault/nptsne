echo ** Start build environment preparation
yum remove -y cmake
yum install -y lz4-devel libXrandr-devel libXinerama-devel libXcursor-devel libXi-devel

PY37_BIN=/opt/python/cp37-cp37m/bin
$PY37_BIN/pip install cmake
ln -s $PY37_BIN/cmake /usr/local/bin/cmake
echo "CMake version:"
cmake --version

$PY37_BIN/pip install -Iv six==1.12.0
$PY37_BIN/pip install conan_package_tools==0.32.2 bincrafters_package_tools==0.26.3
$PY37_BIN/pip install conan==1.24.1
conan=`which conan`; ln -s $PY37_BIN/conan $conan
echo "conan version:"
conan --version
echo ** End build environment preparation