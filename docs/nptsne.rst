====================
nptsne API Reference
====================

Module summary
**************


API Reference
=============

t-SNE classes
   * TextureTsne : linear tSNE simple API

   * TextureTsneExtended : linear tSNE advanced API wrapper with additional functionality

HSNE classes
   * HSne: Hierarchical-SNE model builder

   * HSneScale: Wrapper for a scale in the HSNE model

   
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
