rd /s /q %TMP%\\cibwlibsdir
mkdir %TMP%\\cibwlibsdir 
echo Python version:
python --version
echo CMake version
cmake --version 
echo conan version
conan --version 
echo Prepare conan
conan user 
type %1\\cert.pem >> %USERPROFILE%\\.conan\\cacert.pem
conan remote add -f lkeb-artifactory https://lkeb-artifactory.lumc.nl/artifactory/api/conan/conan-local