Installing and Using
====================

This release supports 3 python versions (3.6, 3.7 and 3.8) on three platforms: Windows, Ubuntu, Macos

On Windows and Linux acceleration is performed using compute shaders. On Macos, due to the lack of compute shader support, tSNE uses a rasterized implementation with a lower performance.

Installing
----------

Windows,MacOS,Linux: install from PyPi using: **pip install nptsne**. `The PyPi page. <https://pypi.org/project/nptsne/>`_

    
Demos
-----

A number of demos have been created to help you exploit the accelerated tSNE and HSNE offered by this package.

.. csv-table:: **Demos**
  :header: "Demo", "Description"
  :widths: 25, 50

  "`HSNE Multi datatype <http://doi.org/10.5281/zenodo.4003503>`_", "| A complete demonstration including 
  | three different datatypes:
  
   - Image is datapoint (MNIST)
   - Pixel is data point (Hyperspectral solar images)
   - Multi-dimensional plus meta data (Genetic data)"
  "`HSNE with Louvain clustering <http://doi.org/10.5281/zenodo.4003503>`_", "| Louvain clustering is applied to 
  | levels in the HSNE hierarchy"
  "`Jupyter notebook for GPU accelerated tSNE  <http://doi.org/10.5281/zenodo.4003503>`_","| A Jupyter notebook demonstration
  | of the tSNE API. 
  | Illustrates a plain tSNE, pre-loaded embedding and 
  | altering the moment when the exaggeration 
  | factor is removed. "

_.

