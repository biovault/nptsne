FROM centos:7 AS qtbuild
ARG BUILDSTATIC
ENV QT_VERSION v5.9.7
ENV QT_CREATOR_VERSION v4.3.1

# Build prerequisites
RUN yum -y update 
RUN yum -y install centos-release-scl
RUN yum -y update 
RUN yum -y install devtoolset-7-gcc-c++* && scl enable devtoolset-7 bash

RUN yum -y install git \
	make \
	python \
    libXext-devel \
    libX11-devel \
	libxcb libxcb-devel xcb-util xcb-util-devel mesa-libGL-devel libxkbcommon-devel \
	epel-release \
	glx-utils sudo


# Other useful tools
RUN yum -y install \
	wget \
	zip \
	vim

# Simple root password in case we want to customize the container
RUN echo "root:root" | chpasswd

RUN useradd -G video -ms /bin/bash user

# dynamic qt + qtcreator
RUN mkdir -p /qt/build
RUN mkdir /qt5

WORKDIR /qt/build

ADD build_qt.sh /qt/build/build_qt.sh
RUN scl enable devtoolset-7 'QT_VERSION=$QT_VERSION QT_CREATOR_VERSION=$QT_CREATOR_VERSION /qt/build/build_qt.sh'

# static qt  
RUN if [ "$BUILDSTATIC" = "True" ] ; then  mkdir -p /qtstatic/build ; fi
RUN if [ "$BUILDSTATIC" = "True" ] ; then  mkdir /qt5static ; fi

WORKDIR /qtstatic/build

ADD build_qt_static.sh /qtstatic/build/build_qt_static.sh
RUN if [ "$BUILDSTATIC" = "True" ] ; then scl enable devtoolset-7 'QT_VERSION=$QT_VERSION /qtstatic/build/build_qt_static.sh' ; fi

USER user

WORKDIR /qt

########################################################################
FROM nvidia/opengl:1.0-glvnd-runtime-centos7
LABEL maintainer "Baldur van Lew"

#Installs dependencies.
RUN yum -y install centos-release-scl
RUN yum -y update
RUN yum group -y install "Development Tools" 
RUN yum -y install devtoolset-7-gcc-c++* && scl enable devtoolset-7 bash

RUN yum -y install \
        sudo \
        glmark2 \
		git \
		python \
		libXext-devel \
		libX11-devel \
		libxcb libxcb-devel xcb-util xcb-util-devel \
		mesa-libGL-devel mesa-libGLU-devel libxkbcommon-devel \
		zlib-devel freeglut-devel \
		epel-release \
		glx-utils  \
		which \
        gdb \
        nano \
        cmake3 cmake3-gui

# Prefer cmake 3
RUN sudo alternatives --install /usr/local/bin/cmake cmake /usr/bin/cmake3 20 \
	--slave /usr/local/bin/ctest ctest /usr/bin/ctest3 \
	--slave /usr/local/bin/cpack cpack /usr/bin/cpack3 \
	--slave /usr/local/bin/ccmake ccmake /usr/bin/ccmake3 \
	--family cmake
  
# specific for hdi project - flann is 1.8.4      
RUN yum -y install \
		flann-devel \
		lz4-devel

# Get the qt build 
RUN mkdir -p ./qt5
RUN if [ "$BUILDSTATIC" = "True" ] ; then mkdir -p ./qt5static ; fi
COPY --from=qtbuild /qt5 ./qt5
# need conditional COPY trick here
#COPY --from=qtbuild /qt5static ./qt5static

#Creates unprivileged user.
COPY /create-user.sh /
RUN chmod +x create-user.sh
ARG docker_root_pass=root
ARG docker_unprivileged_user=glxtest
ARG docker_unprivileged_pass=glxtest
RUN /create-user.sh && \
    rm /create-user.sh

# the sudo group is called wheel on CentOS    
RUN  usermod -a -G wheel glxtest   

USER $docker_unprivileged_user
WORKDIR /home/$docker_unprivileged_user


