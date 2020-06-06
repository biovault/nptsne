"""
nptsne - Numpy compatible tSNE
==============================

A numpy compatible python extension for GPGPU linear complexity t-SNE and h-SNE

This package contains classes that wrap linear complexity t-SNE
and classes to support hierarchical SNE h-SNE.
    
tSNE
----

    TextureTsne : linear tSNE simple API
    TextureTsneExtended : linear tSNE advanced API wrapper with additional functionality

hSNE
----
   
    HSne: Hierarchical-SNE model builder
    HSneScale: Wrapper for a scale in the h-SNE model


Available subpackages
---------------------

hsne_analysis     
    Provides classes for selection driven navigation of the hSNE model and mapping back
    to the original data. The classes are indended to support visual analytics

Notes
-----

:class:`ndarray` types are the preferred parameters types for input 
and where possible internal data in the wrapped t-SNE and h-SNE is returned without 
a copy in a :class:`ndarray`.

References
----------
Linear complexity t-SNE  https://doi.org/10.1109/TVCG.2019.2934307 or (https://arxiv.org/abs/1805.10817v2)
Hierarchical SNE https://doi.org/10.1111/cgf.12878

"""        
from .libs._nptsne import (TextureTsne, TextureTsneExtended, KnnAlgorithm, HSne, HSneScale)
from .version import __version__

__all__ = (
    'TextureTsne', 
    'TextureTsneExtended', 
    'KnnAlgorithm', 
    'HSne',
    'HSneScale',
)