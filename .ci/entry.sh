wget -O miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sudo bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
conda config --set always_yes yes --set changeps1 no
conda config --add channels conda-forge
conda update -q conda
conda install -q conda-build
echo Creating conda env for python version $CONAN_LINUX_PYTHON
conda create -q -n build_env python=$CONAN_LINUX_PYTHON
source activate build_env  
conda install -n build_env cmake
conda install -c conda-forge conan 
conda install -c conda-forge scikit-build
pip install conan_package_tools bincrafters_package_tools
echo Conda python version `python --version`
 
