Installing and Using
====================

This release supports 2 python versions (3.6 or 3.7) on three platforms: Windows, Ubuntu, Macos

On Windows and Linux acceleration is performed using compute shaders. On Macos, due to the lack of compute shader support, tSNE uses a rasterized impplementation with a lower performance.

Installing
----------

Windows and MacOS: install from PyPi using: **pip install nptsne**. `The PyPi page. <https://test.pypi.org/project/nptsne/>`_

Linux: (only Ubuntu (16.06 and upward) is supported). Download the correct file (see below) for your python version and install using **pip install <file>.whl**

.. csv-table:: Ubuntu whl files
   :header: "py36", "py37"
   :widths: 40, 40

    :linux_whl_url:`Ubuntu py36 <36>`, :linux_whl_url:`Ubuntu py37 <37>`
    
Examples
--------

Examples of both the :py:class:`nptsne.TextureTsne` and :py:class:`nptsne.TextureTsneExtended` are available in a
`Jupyter notebook <http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/NPTSNE_notebooktests.ipynb>`_.

 



