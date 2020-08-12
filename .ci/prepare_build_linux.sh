echo ** Start build environment preparation
yum remove -y cmake
yum install -y lz4-devel libXrandr-devel libXinerama-devel libXcursor-devel libXi-devel
pip install -Iv six==1.12.0
pip install conan_package_tools==0.32.2 bincrafters_package_tools==0.26.3
echo ** End build environment preparation

