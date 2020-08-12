set -x
echo ** Start build environment preparation
yum remove -y cmake
yum install -y lz4-devel libXrandr-devel libXinerama-devel libXcursor-devel libXi-devel

pip install cmake
ln -s `which cmake` /usr/local/bin/cmake
echo "CMake version:"
cmake --version

pip install -Iv six==1.12.0
pip install conan_package_tools==0.32.2 bincrafters_package_tools==0.26.3
pip install conan==1.24.1
ln -s `which conan` /usr/local/bin/conan
echo "conan version:"
conan --version
echo ** End build environment preparation