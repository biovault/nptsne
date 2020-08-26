====================
nptsne API Reference
====================

Module summary
**************


nptsne - Numpy compatible tSNE
==============================

A numpy compatible python extension for GPGPU linear complexity t-SNE and HSNE

This package contains classes that wrap linear complexity *t-SNE*
and classes to support *HSNE*.

t-SNE classes
   * TextureTsne : linear tSNE simple API

   * TextureTsneExtended : linear tSNE advanced API wrapper with additional functionality

HSNE classes
   * HSne: Hierarchical-SNE model builder

   * HSneScale: Wrapper for a scale in the HSNE model


Available subpackages
---------------------

hsne_analysis
   Provides classes for selection driven navigation of the HSNE model and mapping back
   to the original data. The classes are indended to support visual analytics

.. note:: Numpy compatibility: 
   ``ndarray`` types are the preferred parameters types for input
   and where possible internal data in the wrapped t-SNE and HSNE is returned without
   a copy in a ``ndarray``.


References
----------

   * `Linear complexity t-SNE  <https://doi.org/10.1109/TVCG.2019.2934307>`_ or (`Linear complexity t-SNE (Preprint) <https://arxiv.org/abs/1805.10817v2>`_)
   * `Hierarchical SNE <https://doi.org/10.1111/cgf.12878>`_

   
``nptsne``: t-SNE and HSNE data embedding
==========================================


.. autosummary::
   :nosignatures:

   nptsne.HSne
   nptsne.HSneScale
   nptsne.TextureTsne
   nptsne.TextureTsneExtended
   nptsne.KnnAlgorithm
   
.. automodule:: nptsne
    :members:
    :no-inherited-members:
    :no-imported-members:
    :exclude-members: __weakref__, __doc__, __module__, __dict__, __members__, __getstate__, __setstate__


``nptsne.hsne_analysis``: HSNE analysis support submodule
==========================================================

.. autosummary::
   :nosignatures:

   nptsne.hsne_analysis.Analysis
   nptsne.hsne_analysis.AnalysisModel
   nptsne.hsne_analysis.EmbedderType
   nptsne.hsne_analysis.SparseTsne
   
.. automodule:: nptsne.hsne_analysis
    :members:
    :no-inherited-members:
    :no-imported-members:
    :exclude-members: __weakref__, __doc__, __module__, __dict__, __members__, __getstate__, __setstate__
