#### NVIDIA dockers for build/test

1.) Use the scripts in the sub-directories docker-qt-ubunt and in docker-qt-centos to build docker images with a build of Qt5.9.7. 

2) One level below the docker_qt_conda directories extend these images with miniconda python3.6 and 3.7 suitable for the python build or test. The current python build actually used the qt from miniconda rather than the self built. 

**TODO** for performance reasons eliminate the self-build Qt step.

#### NVIDIA docker plugin 
The docker environment must have the [NVIDIA docker plugin](https://github.com/NVIDIA/nvidia-docker/wiki/nvidia-docker-plugin) installed. 