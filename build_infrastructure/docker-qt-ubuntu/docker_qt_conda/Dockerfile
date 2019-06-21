FROM ubuntu1604/qt597
LABEL maintainer="Baldur van Lew"

# The username that is used for development
ARG USERNAME

USER root
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y \
	wget

# Switch to the development user
USER $USERNAME

RUN /bin/bash -c 'echo Home is $HOME && mkdir $HOME/installers'
WORKDIR /home/$USERNAME/installers

# get and install miniconda, setup conda in the bashrc
RUN /bin/bash -c 'cd $HOME/installers && \
	wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
	chmod +x $HOME/installers/Miniconda3-latest-Linux-x86_64.sh && \
	$HOME/installers/Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/anaconda3 && \
	echo "export PATH=$HOME/anaconda3/bin:$PATH"'
	
RUN /bin/bash -c 'source $HOME/.bashrc; $HOME/anaconda3/bin/conda init bash'	
    
RUN /bin/bash -c 'source $HOME/.bashrc; $HOME/anaconda3/bin/conda create -y -n py36 python=3.6'
RUN /bin/bash -c 'source $HOME/.bashrc; $HOME/anaconda3/bin/conda create -y -n py37 python=3.7'

RUN /bin/bash -c 'source $HOME/.bashrc; source $HOME/anaconda3/bin/activate py36 && $HOME/anaconda3/bin/conda install numpy scipy matplotlib && pip install scikit-build' 
RUN /bin/bash -c 'source $HOME/.bashrc; source $HOME/anaconda3/bin/activate py37 && $HOME/anaconda3/bin/conda install numpy scipy matplotlib && pip install scikit-build' 
