rd /s /q %TMP%\\cibwlibsdir
mkdir %TMP%\\cibwlibsdir 
pip install --upgrade pip
pip install -r requirements.txt
echo Python version:
python --version
echo CMake version
cmake --version 
echo conan version
conan --version 
echo Prepare conan
conan user 
type %1\\cert.pem >> %USERPROFILE%\\.conan\\cacert.pem 
conan remote add -f bincrafters https://api.bintray.com/conan/bincrafters/public-conan