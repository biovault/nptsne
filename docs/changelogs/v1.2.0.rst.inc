Version 1.2.0
-----------------
Supports python 3.6, 3.7, 3.8, 3.9 on Windows, Ubuntu (using manylinux2010) and Macos.

Changelog 1.2.0
~~~~~~~~~~~~~~~
- Using the latest `HDI Library <http://github.com/biovault/HDILib>`_ 
  v1.2.2 supporting the additional Annoy knn method.

- Added KnnDistanceMetric to the TextureTsne and TextureTsneExtended classes

- Added a fast, non-exact implementation of the algorithm to get an area of
  interest from a landmark based selection at :py:meth:`nptsne.hsne_analysis.Analysis.get_fast_area_of_influence`.
  The algorithm pre-calculates a set of non-overlapping AOIs for each landmark at an HSNE scale.
  For the correct AOI (according to the [NP2019]_) use the slower :py:meth:`nptsne.hsne_analysis.Analysis.get_area_of_influence`.

- An additional demo set (DC Mall) has been added to the data and the |EXHSNEdemo_github_url|
  was updated to allow the display of a background image. See :ref:`Demo list`

- nptsne has added typing as specified in `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_.
  The demos have also been extended to use PEP 484. Types are included in the package using __init__.pyi
  files as specified in `PEP 561 <https://www.python.org/dev/peps/pep-0561/>`_. 