====================
nptsne API Reference
====================

Module summary
**************


nptsne - Numpy compatible tSNE
==============================

A numpy compatible python extension for GPGPU linear complexity t-SNE and h-SNE

This package contains classes that wrap linear complexity *t-SNE*
and classes to support *h-SNE*.

t-SNE classes
   * TextureTsne : linear tSNE simple API

   * TextureTsneExtended : linear tSNE advanced API wrapper with additional functionality

h-SNE classes
   * HSne: Hierarchical-SNE model builder

   * HSneScale: Wrapper for a scale in the h-SNE model


Available subpackages
---------------------

hsne_analysis
   Provides classes for selection driven navigation of the hSNE model and mapping back
   to the original data. The classes are indended to support visual analytics

-[ Notes ]-

``ndarray`` types are the preferred parameters types for input
and where possible internal data in the wrapped t-SNE and h-SNE is returned without
a copy in a ``ndarray``.


-[ References ]-

Linear complexity t-SNE  `https://doi.org/10.1109/TVCG.2019.2934307 <https://doi.org/10.1109/TVCG.2019.2934307>`_ or (`https://arxiv.org/abs/1805.10817v2 <https://arxiv.org/abs/1805.10817v2>`_)
Hierarchical SNE `https://doi.org/10.1111/cgf.12878 <https://doi.org/10.1111/cgf.12878>`_

   
``nptsne``: t-SNE and h-SNE data embedding
==========================================

.. automodule:: nptsne
    :members:
    :no-inherited-members:
    :no-imported-members:
    :exclude-members: __weakref__, __doc__, __module__, __dict__, __members__, __getstate__, __setstate__


``nptsne.hsne_analysis``: h-SNE analysis support submodule
==========================================================

.. automodule:: nptsne.hsne_analysis
    :members:
    :no-inherited-members:
    :no-imported-members:
    :exclude-members: __weakref__, __doc__, __module__, __dict__, __members__, __getstate__, __setstate__
