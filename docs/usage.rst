Installing and Using
====================

This release supports 3 python versions (3.6,3.7 and 3.8) on three platforms: Windows, Ubuntu, Macos

On Windows and Linux acceleration is performed using compute shaders. On Macos, due to the lack of compute shader support, tSNE uses a rasterized implementation with a lower performance.

Installing
----------

Windows,MacOS,Linux: install from PyPi using: **pip install nptsne**. `The PyPi page. <https://pypi.org/project/nptsne/>`_

    
Examples
--------

Examples of both the :py:class:`nptsne.TextureTsne` and :py:class:`nptsne.TextureTsneExtended` are available in a
`Jupyter notebook <http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/NPTSNE_notebooktests.ipynb>`_.

