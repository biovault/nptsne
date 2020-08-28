"""
A numpy compatible python extension for GPGPU linear complexity t-SNE and HSNE

This package contains classes that wrap linear complexity *t-SNE*
and classes to support *HSNE*.
    
Available subpackages
---------------------

hsne_analysis
   Provides classes for selection driven navigation of the HSNE model and mapping back
   to the original data. The classes are intended to support visual analytics

Notes
-----
:class:`ndarray` types are the preferred parameters types for input 
and where possible internal data in the wrapped t-SNE [1]_ and HSNE [2]_ is returned without 
a copy in a :class:`ndarray`.

References
----------
.. [1] Pezzotti, N. et al., `GPGPU Linear Complexity t-SNE Optimization <https://doi.org/10.1109/TVCG.2019.2934307>`_
.. [2] Pezzotti, N. et al., `Hierarchical Stochastic Neighbor Embedding <https://doi.org/10.1111/cgf.12878>`_

"""        
from .libs._nptsne import (TextureTsne, TextureTsneExtended, KnnAlgorithm, HSne, HSneScale)
from .version import __version__
from . import hsne_analysis

__all__ = (
    'TextureTsne', 
    'TextureTsneExtended', 
    'KnnAlgorithm', 
    'HSne',
    'HSneScale',
    'hsne_analysis'
)
