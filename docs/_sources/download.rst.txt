Usage
=========

This release supports 2 python versions (3.6 or 3.7) on three platforms: Windows, Ubuntu, Macos

On Windows and Linux acceleration is performed using compute shaders. On Macos, due to the lack of compute shader support, tSNE uses a rasterized impplementation with a lowe performance.

Installing
----------

WIndows and MacOS: install from PyPi using: **pip install nptsne**. 

Linux: (only Ubuntu (16.06 and upward) is supported). Download the correct file (see below) for your python version and install using **pip install <file>.whl**

.. csv-table:: Ubuntu whl files
   :header: "py36", "py37"
   :widths: 40, 40

    `Ubuntu py36 wheel <http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/nptsne-1.0.0rc3-cp36-none-linux_x86_64.whl>`_, `Ubuntu py37 wheel <http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/nptsne-1.0.0rc3-cp37-none-linux_x86_64.whl>`_



Examples
--------

Example of both the :py:class:`nptsne.TextureTsne` and :py:class:`nptsne.TextureTsneExtended` are available in a
`Jupyter notebook <http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/NPTSNE_notebooktests.ipynb>`_.


umap to tSNE example
~~~~~~~~~~~~~~~~~~~~

This short animation shows the effect of inputting a umap embedding of 7000 MNIST digits into tSNE and then
relaxing the force exaggeration.

.. raw:: html

    <img src="https://drive.google.com/uc?export=view&id=1fW4IHOyio59Yx59wcpbpQrMl_ZiIlIet"/>


