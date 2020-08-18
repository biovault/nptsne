echo Python version:
python --version 
echo CMake version
cmake --version
echo conan version
conan --version
echo Prepare conan
conan user
conan remote add -f bincrafters https://api.bintray.com/conan/bincrafters/public-conan
export GIT_DERIVED_BUILD_NUMBER=`python3 get_git_derived_build_number.py feature/cibuild ./src/nptsne/_version.txt`