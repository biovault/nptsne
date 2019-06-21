#! /bin/sh

nvidia-docker build --no-cache --build-arg USERNAME=glxtest -t ubuntu1604/qt597_pybuild .
