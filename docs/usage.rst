Installing and Using
====================

This release supports 3 python versions (3.6, 3.7 and 3.8) on three platforms: Windows, Ubuntu, Macos

On Windows and Linux acceleration is performed using compute shaders. On Macos, due to the lack of compute shader support, tSNE uses a rasterized implementation with a lower performance.

Installing
----------

Windows,MacOS,Linux: install from PyPi using: **pip install nptsne**. `The PyPi page. <https://pypi.org/project/nptsne/>`_


Demo list
---------

A number of demos have been created to help you exploit the accelerated tSNE and HSNE offered by this package.

.. list-table:: Demos
   :widths: 25, 50
   :header-rows: 1

   * - Demo
     - Description
   * - `HSNE Multi datatype <http://doi.org/10.5281/zenodo.4003503>`_
     - .. line-block::
         A complete demonstration including 
         three different datatypes: 
         * Image is datapoint (MNIST)
         * Pixel is data point (Hyperspectral solar images)
         * Multi-dimensional plus meta data (Genetic data)
   * - `HSNE with Louvain clustering <http://doi.org/10.5281/zenodo.4003503>`_
     - | Louvain clustering applied to 
       | levels in the HSNE hierarchy
   * - `Jupyter notebook for GPU accelerated tSNE  <http://doi.org/10.5281/zenodo.4003503>`_
     - .. line-block::
         A Jupyter notebook demonstration
         of the tSNE API. 
         Illustrates the following options: 
         * a plain tSNE
         * a pre-loaded embedding
         * controlling the iteration when the 
           exaggeration factor is removed.


