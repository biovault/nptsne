.. _nptsne-api-label:

====================
nptsne API Reference
====================

Module summary
**************


API Reference
=============

.. currentmodule:: nptsne

The main API classes are:

t-SNE classes
   * :class:`TextureTsne` : linear tSNE simple API
   * :class:`TextureTsneExtended` : linear tSNE advanced API wrapper with additional functionality

HSNE classes
   * :class:`HSne` : Hierarchical-SNE model builder
   * :class:`HSneScale` : Wrapper for a scale in the HSNE model

Full details are in the reference below.

Code examples
=============

The *Examples* in the documentation make use of the DocTest run_doctest.py to prepare the sample data. 
Refer to either the repository code |doctest_github_url| or :ref:`demo_list-label` for more information.

``nptsne``: t-SNE and HSNE data embedding
==========================================

.. autosummary::
   :nosignatures:

   HSne
   HSneScale
   TextureTsne
   TextureTsneExtended
   KnnAlgorithm
   
.. automodule:: nptsne
    :members:
    :no-inherited-members:
    :no-imported-members:
    :exclude-members: __weakref__, __doc__, __module__, __dict__, __members__, __getstate__, __setstate__


``nptsne.hsne_analysis``: HSNE visual analysis support submodule
================================================================

.. autosummary::
   :nosignatures:

   hsne_analysis.Analysis
   hsne_analysis.AnalysisContainer
   hsne_analysis.AnalysisModel
   hsne_analysis.EmbedderType
   hsne_analysis.SparseTsne
   
.. automodule:: nptsne.hsne_analysis
    :members:
    :no-inherited-members:
    :no-imported-members:
    :exclude-members: __weakref__, __doc__, __module__, __dict__, __members__, __getstate__, __setstate__
