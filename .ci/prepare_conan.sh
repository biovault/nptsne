echo Python version:
python --version 
echo CMake version
cmake --version
echo conan version
conan --version
echo Prepare conan
conan user
conan remote add bincrafters https://api.bintray.com/conan/bincrafters/public-conan
