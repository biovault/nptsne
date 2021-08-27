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
cat $1/cert.pem >> ~/.conan/cacert.pem 
conan remote add -f lkeb-artifactory https://lkeb-artifactory.lumc.nl/artifactory/api/conan/conan-local