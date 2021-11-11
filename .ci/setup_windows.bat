echo Python version:
python --version
echo CMake version
cmake --version 
conan --version 
python -m pip install conan==1.41.0 --force
type %CD%\\cert.pem >> %CD%\\.conan\\cacert.pem
conan remote add -f lkeb-artifactory https://lkeb-artifactory.lumc.nl/artifactory/api/conan/conan-local"