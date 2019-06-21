FROM ubuntu:16.04 AS qtbuild
ARG BUILDSTATIC
ENV QT_VERSION v5.9.7
ENV QT_CREATOR_VERSION v4.3.1

# Build prerequisites
RUN apt-get -y update && apt-get -y install qtbase5-dev \
	libxcb-xinerama0-dev \
	build-essential \
	python \
	sudo \
    glmark2 \
	mesa-utils &&\
	rm -rf /var/lib/apt/lists/*

# Other useful tools
RUN apt-get -y update && apt-get -y install tmux \
	wget \
	zip \
	git \
	vim && \
	rm -rf /var/lib/apt/lists/*

# Simple root password in case we want to customize the container
RUN echo "root:root" | chpasswd

RUN useradd -G video -ms /bin/bash user

# dynamic qt + qtcreator
RUN mkdir -p /qt/build
RUN mkdir /qt5

WORKDIR /qt/build

ADD build_qt.sh /qt/build/build_qt.sh
RUN QT_VERSION=$QT_VERSION QT_CREATOR_VERSION=$QT_CREATOR_VERSION /qt/build/build_qt.sh

# static qt - no qtcreator
RUN if [ "$BUILDSTATIC" = "True" ] ; then  "mkdir -p /qtstatic/build ; fi
RUN if [ "$BUILDSTATIC" = "True" ] ; then   mkdir /qt5static ; fi

WORKDIR /qtstatic/build

ADD build_qt_static.sh /qtstatic/build/build_qt_static.sh
RUN if [ "$BUILDSTATIC" = "True" ] ; then  RUN QT_VERSION=$QT_VERSION /qtstatic/build/build_qt_static.sh ; fi

USER user

WORKDIR /qt

########################################################################
FROM nvidia/opengl:1.0-glvnd-runtime-ubuntu16.04
LABEL maintainer "Corey Ryan Hanson"

#Installs dependencies.
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y \
        sudo \
        glmark2 \
        mesa-utils \
        build-essential \
        mesa-common-dev \
        libglu1-mesa-dev \
        freeglut3 freeglut3-dev \
        zlib1g-dev \
        liblz4-dev \
        libflann-dev \
        patchelf \
        chrpath \
        apt-file \
        gdb \
        git-core \
        cmake cmake-gui-qt && \
    rm -rf /var/lib/apt/lists/*

# Get the qt build 
RUN mkdir -p ./qt5
RUN mkdir -p ./qt5static
COPY --from=qtbuild /qt5 ./qt5
COPY --from=qtbuild /qt5static ./qt5static

#Creates unprivileged user.
COPY /create-user.sh /
RUN chmod +x create-user.sh
ARG docker_root_pass=root
ARG docker_unprivileged_user=glxtest
ARG docker_unprivileged_pass=glxtest
RUN /create-user.sh && \
    rm /create-user.sh
    
RUN  usermod -a -G sudo glxtest   
RUN  apt update
RUN  apt-file update

USER $docker_unprivileged_user
WORKDIR /home/$docker_unprivileged_user


