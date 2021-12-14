Installing and Using
====================

This release supports 4 python versions (3.6, 3.7, 3.8, 3.9) on three platforms: Windows, Ubuntu, Macos

On Windows and Linux acceleration is performed using compute shaders. On Macos, due to the lack of compute shader support, tSNE uses a rasterized implementation with a lower performance.

Installing
----------

Windows,MacOS,Linux: install from PyPi using: **pip install nptsne**. `The PyPi page. <https://pypi.org/project/nptsne/>`_


Demo list
---------

A number of demos have been created to help you exploit the accelerated tSNE and HSNE offered by this package. The demos are available in a single `demos.zip <http://doi.org/10.5281/zenodo.4003503>`_ file.

.. list-table:: Demos
   :widths: 25, 50
   :header-rows: 1

   * - Demo
     - Description
   * - `Basic HSNE demo <http://doi.org/10.5281/zenodo.4003503>`_
     - | A limited demo showing HSNE visual 
       | analytics on the *mnist* data set
   * - `Extended HSNE demo <http://doi.org/10.5281/zenodo.4003503>`_
     - .. line-block::
         A complete demonstration including 
         three different datatypes: 
         * Image is datapoint (MNIST)
         * Pixel is data point (Hyperspectral solar images)
         * Multi-dimensional plus meta data (Genetic data)
   * - `HSNE Louvain Demo <http://doi.org/10.5281/zenodo.4003503>`_
     - | Louvain clustering applied to 
       | levels in the HSNE hierarchy
   * - `TextureTsne <http://doi.org/10.5281/zenodo.4003503>`_
     - | GPU accelerated t-SNE 
       | on 70000 MNIST points 
   * - `TextureTsneExtended <http://doi.org/10.5281/zenodo.4003503>`_
     - | GPU accelerated t-SNE 
       | on 70000 MNIST points
       | with intermediate results   
   * - `DocTest <http://doi.org/10.5281/zenodo.4003503>`_
     - | Run the internal doctest examples in nptsne
       | Can be used for install verification     
   * - `Jupyter notebook for GPU accelerated tSNE  <http://doi.org/10.5281/zenodo.4003503>`_
     - .. line-block::
         A Jupyter notebook demonstration
         of the tSNE API. 
         Illustrates the following options: 
         * a plain tSNE
         * a pre-loaded embedding
         * controlling the iteration when the 
           exaggeration factor is removed.


