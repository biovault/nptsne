Installing
==========

This release supports 4 python versions (3.9, 3.10, 3.11, 3.12, 3.13) on three platforms: Windows, Ubuntu, Macos (arm64 only)

On Windows and Linux acceleration is performed using compute shaders. On Macos, due to the lack of compute shader support, tSNE uses a rasterized implementation with a lower performance. Macos testing was restricted to a conda install.

Windows,MacOS,Linux: install from PyPi using: **pip install nptsne**. `The PyPi page. <https://pypi.org/project/nptsne/>`_



