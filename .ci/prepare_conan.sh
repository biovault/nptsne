echo Python version:
python --version 
echo CMake version
cmake --version
echo conan version
conan --version
echo Prepare conan
conan user
cat cert.pem >> ~/.conan/cacert.pem
conan remote add -f bincrafters https://api.bintray.com/conan/bincrafters/public-conan
