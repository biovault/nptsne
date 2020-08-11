echo ** Start build environment preparation
yum remove -y cmake
yum install -y lz4-devel libXrandr-devel libXinerama-devel libXcursor-devel libXi-devel
pip install six==1.12.0
pip install conan==1.24.1 
pip install conan_package_tools==0.32.2 bincrafters_package_tools==0.26.3
echo Python version:
python --version 
pip install cmake
echo CMake version
cmake --version
echo Prepare conan
conan user
conan remote add bincrafters https://api.bintray.com/conan/bincrafters/public-conan
echo ** End build environment preparation

