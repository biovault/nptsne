#! /bin/sh

nvidia-docker build --no-cache --build-arg USERNAME=glxtest -t centos7/qt597_pybuild .
