Usage
=========

This release supports 2 python versions (3.6 or 3.7) on three platforms: Windows, Ubuntu, Macos

On Windows and Linux acceleration is performed using compute shaders. On Macos, due to the lack of compute shader support, tSNE uses a rasterized impplementation with a lowe performance.

Installing
----------

Download the correct file file for your OS and python version and install with pip install <file>.whl

.. csv-table:: Windows whl files
   :header: "py36", "py37"
   :widths: 40, 40

    `nptsne-0.2.0-cp36-cp36m-win_amd64.whl <https://drive.google.com/uc?export=download&id=1OOIazZ-VGDwi64EB5JWxN2eXlcfKMlbJ>`_, `nptsne-0.2.0-cp37-cp37m-win_amd64.whl <https://drive.google.com/uc?export=download&id=1f2ra9r4fOq-F3PKo5jAF1aEcpI7CaDje>`_


.. csv-table:: Ubuntu whl files
   :header: "py36", "py37"
   :widths: 40, 40

    `Ubuntu nptsne-0.1.1-cp36-cp36m-linux_x86_64.whl <https://drive.google.com/uc?export=download&id=1UfRm1fLprY7Bkt49HaKi8_710klXU7eA>`_, `Ubuntu nptsne-0.1.1-cp37-cp37m-linux_x86_64.whl <https://drive.google.com/uc?export=download&id=1lzPtOVZ8QlhdtyoyWKYeC9ZWQz1s1b1G>`_


.. csv-table:: CentOS whl files [1]_
   :header: "py36", "py37"
   :widths: 40, 40

    `CentOS nptsne-0.1.1-cp36-cp36m-linux_x86_64.whl <https://drive.google.com/uc?export=download&id=14t5hTO8ju7f3wfa3JUbVZ3XDqZmyy1PA>`_, `CentOS nptsne-0.1.1-cp37-cp37m-linux_x86_64.whl <https://drive.google.com/uc?export=download&id=1cG_rd8Wj_suLjfn6c-6ANNaUNPdluEvV>`_


Examples
--------

Example of both the :py:class:`nptsne.TextureTsne` and :py:class:`nptsne.TextureTsneExtended` are available in this
examples package both as `(zipped) python files <https://drive.google.com/uc?export=download&id=1uuopX-hj25xl0nwSJIJkRaTLEEXotrrQ>`_ or bundled in a
`Jupyter notebook <https://drive.google.com/uc?export=download&id=1xDZQZtZp3a9o5wHcB22l3ST72hLLZebv>`_.


umap to tSNE example
~~~~~~~~~~~~~~~~~~~~

This short animation shows the effect of inputting a umap embedding of 7000 MNIST digits into tSNE and then
relaxing the force exaggeration.

.. raw:: html

    <img src="https://drive.google.com/uc?export=view&id=1fW4IHOyio59Yx59wcpbpQrMl_ZiIlIet"/>



.. [1] CentOS issue

    Fixing problems with libpng16

    If python on Centos reports problems with libpng16 download and untar
    `libpng16.so.tar.xz <https://drive.google.com/uc?export=download&id=1xNuCtqGmgW1Ctq-IDwVcLpGSAuKM8cof>`_
    and copy the contents to the site-packages/nptsne directory.

    This is a known deployment issue and will be fixed in a future release.
