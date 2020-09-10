# This build information is deprecated but preserved for future reference


# Build with conan
This repository is configured too build Window, Linux and Macos using conan and the Appveyor and Travis CIs. The build is done via the conanfile which can also be run manually.

0. Make and select a python virtual env for py36 or 37 (can use miniconda or virtualenv). Make sure that the correct compiler is available.
1. Pip install conan==1.19.3
2. Intialize conan with  `conan user`
3. Pip install conan_package_tools==0.29.3 bincrafters_package_tools==0.21.0
4. Clone and checkout the nptsne branch
5. cd to the nptsne directory and create with conan ` conan create . nptsne/<version>@<yourname>/develop` `<version>` must match the version in the conanfile.py. You are free to choose another channel name (here "develop" is suggested. If you intend to deploy your build as stable to the Artifactory you might prefer `nptsne/<version>@<yourorganisationname>/stable`

The CI/CD is configured to use conan.

For more information about conan see the [conan docs](https://docs.conan.io/en/latest/).

## Information only: Old manual build system

What follows is the previous manual build system
#### <span style="font-size:1.5em;">Instructions for manual building/testing</span>

(for CI/CD see elsewhere)

## Prerequisites

Development tools (above build-essential)

```
sudo apt-get install cmake
sudo apt-get install cmake-qt-gui (optional)
sudo apt-get install liblz4-dev
sudo apt-get install liblz4-tool (optional)
sudo apt-get install libgl-dev
```

Extra python packages for your 3.6 and 3.7 (assuming an anaconda environment as default)

- numpy
- scipy
- matplotlib
- scikit-build


##Building

1. add cmake to the path (e.g. set PATH=%PATH%;C:\Program Files\CMake\bin)
2. Provide the build locations for the FLANN and HDI libraries
3. To get pybind11 (in the absence of a recursive clone of the main repo) remember to
```
git submodule init
git submodule update
```
4) Building (paths from windows example)

Note the full path for the flann lib (relative won't work with the linker)

#### WINDOWS Build:
**Note:** *If errors occur with skbuild and cmake do pip install cmake in the py3x environment*

First cleanup the previous build
>```cleanup.bat```

**py3.7**

4.a) ```conda activate Py37```

**py3.6**

4.a) ```conda activate Py36```

4.b)
```
pip install cmake
python setup.py bdist_wheel -- -DFLANN_BUILD_DIR=G:/Projects/3rdParty/flann/bld/lib -DHDI_INCLUDE_ROOT=G:/Projects/tsne_py/TextureTSNE -DHDI_BLD_ROOT=G:/Projects/tsne_py/TextureTSNE/bld/hdi
```

#### LINUX Build:

First cleanup the previous build
```./cleanup.sh```

**CENTOS only**

4.a) ```scl enable devtoolset-7```

_Either py3.6_

4.b) ```conda activate py36```

_Or py3.7_

4.b) ```conda activate py37```

4.c) ```python setup.py bdist_wheel --```


5) Testing - use a separate python environment (preferable a separate machine)
pip install dist37 or dist36\\<pkgname\>.whl

5a) Use 'behave' BDD test on the test features.

## Building/Testing Linux on AWS

The following is a recipe for setting up  a device image for testing or building on Amazon AWS. Undoubtedly this could be adapted to Azure or Google Cloud

#### Choosing the hardware needed

To test we need an instance with graphics hardware. For Windows instances Amazon Elastic Graphics supports on demand GPU usage, however, at the time of writing (June 2019), this is not supported for Linux. As a result the instance should be chosen from the following:

__EC2 Instance Types with  NVIDIA TESLA GPUs (p & g types - June 2019)__
- p2.xlarge
- p2.8xlarge
- p2.16xlarge
- p3.2xlarge
- p3.8xlarge
- p3.16xlarge
- g2.2xlarge
- g2.8xlarge
- g3.4xlarge
- g3.8xlarge

g2.2xlarge is the cheapest but the performance of large tSNE can be quite slow, g3.4xlarge is a good compromise.  Not all types are available in all regions.

#### Spot instances
On AWS use spot instances to save on costs. The Choosing a regoin in a night time zone seems to increase the chances of availability (e.g. from the Netherlands - N.California appears to be a good option).  g3.4xlarge can generally be obtained on spot (June 2019) at approx $0.65 per hour, g2.2xlarge for $0.21.

Spots can be allocated in blocks from 1 to 6 hours but can also be prematurely terminated. Use a running spot instance to create an image following the recipe below

#### Building a Centos7 with latest NVIDIA drivers

1. Search the AWS marketplace for a suitable base image. In this case "CentOS 7 (x86_64) - with Updates HVM"
2. Going to the configuration page you can select a region and discover the AMI Id in that region.
3. Launch a spot instance with graphics hardware  (for unlimited or unlimited time)
4. ssh to the instance with your private key and follow the following:

```
sudo yum erase nvidia cuda
# if needed sudo reboot
sudo yum install -y gcc kernel-devel-$(uname -r)
cat << EOF | sudo tee --append /etc/modprobe.d/blacklist.conf
blacklist vga16fb
blacklist nouveau
blacklist rivafb
blacklist nvidiafb
blacklist rivatv
EOF
sudo echo "GRUB_CMDLINE_LINUX="rdblacklist=nouveau" >> /etc/default/grub
sudo grub2-mkconfig -o /boot/grub2/grub.cfg

aws s3 --no-sign-request cp --recursive s3://ec2-linux-nvidia-drivers/latest/ .
sudo /bin/sh ./NVIDIA-Linux-x86_64*.run
sudo reboot

nvidia-smi -q | head

# install epel repo
sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

# install X stuff
sudo yum install xorg*
sudo yum install mesa-libGLU.x86_64
sudo yum install glx-utils
# Not really necessary
sudo yum install xorg-x11-apps

# set up the xorg conf - busid from nvidia-smi (convert to decimal is needed.
# The example here is a g3.4large which typically has a bus-id of 0:30:0 decimale or 0:1e:0 hex
sudo nvidia-xconfig --busid="0:30:0" --allow-empty-initial-configuration --virtual=1920x1080 --use-display-device=0

# Run X and check that the drivers are picked up
sudo X :0 &
export DISPLAY=:0
glxinfo | grep OpenGL

# Install python with Miniconda

https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh

conda create -n py36 anaconda python=3.6
pip install scikit-build
conda create -n py37 anaconda python=3.7
pip install scikit-build

# ref http://www.libpng.org/pub/png/libpng.html
wget http://slackware.osuosl.org/slackware64-current/slackware64/l/libpng-1.6.37-x86_64-1.txz
tar xvf libpng-1.6.37-x86_64-1.txz
cp ./usr/lib64/libpng16.so.16.37.0 /home/centos/miniconda2/envs/py36/lib/
cp ./usr/lib64/libpng16.so.16.37.0 /home/centos/miniconda2/envs/py37/lib/
```

References

1. [Installing latest graphics drivers on AWS instance]( https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/install-nvidia-driver.html)
2. [Setting up a graphics environment on an EC2 instance](https://kitware.github.io/paraviewweb/docs/graphics_on_ec2_g2.html)

###### <span style="font-size:1.5em;">Save as an AMI</span>
Save the instance to a private AMI that can be used to launch a new spot instance.


#### Building a Ubuntu 16.04 with latest NVIDIA drivers

As CentOS but:

1. use sudo apt-get install instead of yum
2. sudo apt-get install build-essential  (gcc 5.4 - supports stdc++14)
