echo ** Start build environment preparation
yum remove -y cmake
yum install -y lz4-devel libXrandr-devel libXinerama-devel libXcursor-devel libXi-devel
echo ** End build environment preparation

