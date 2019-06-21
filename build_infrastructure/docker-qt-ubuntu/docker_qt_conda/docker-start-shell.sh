#! /bin/sh

# Fix for running GUI programs from within the docker container:
#
# Make xorg disable access control, i.e. let any x client connect to our
# server.
xhost +

nvidia-docker start ubuntu1604-pybsh --attach --interactive
