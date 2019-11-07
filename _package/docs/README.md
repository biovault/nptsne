### nptsne - A numpy compatible python extension for GPGPU linear complexity tSNE

The nptsne package is designed to export a number of python classes that
wrap GPGPU linear complexity tSNE
implementations based on the following publications
[DOI: 10.1109/TVCG.2019.2934307](https://doi.org/10.1109/TVCG.2019.2934307) or the [arXiv preprint](https://arxiv.org/abs/1805.10817v2)

When using nptsne please include the following citation:

*N. Pezzotti et al., "GPGPU Linear Complexity t-SNE Optimization," in IEEE Transactions on Visualization and Computer Graphics.\
doi: 10.1109/TVCG.2019.2934307\
keywords: {Minimization;Linear programming;Computational modeling;Approximation algorithms;Complexity theory;Optimization;Data visualization;High Dimensional Data;Dimensionality Reduction;Progressive Visual Analytics;Approximate Computation;GPGPU},\
URL: http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8811606&isnumber=4359476*

##### Attributions

The tSNE implementations are the original work of the authors named in the literature.

###### Full documentation

Full documentation is available at the [nptsne doc pages](https://biovault.github.io/nptsne/nptsne.html)

##### Wrapper classes

Class | Description | Doc link
---  | --- | ---
TextureTsne | Linear time tSNE reliant on GPU textures | https://biovault.github.io/nptsne/nptsne.html#nptsne.TextureTsne
TextureTsneExtended | Linear time tSNE reliant on GPU textures, extended API | https://biovault.github.io/nptsne/nptsne.html#nptsne.TextureTsneExtended

##### Linux support
Linux: (only Ubuntu 16.06 and upward is supported). Download the correct file (see below) for your python version and install using **pip install <file>.whl**

| py36 | py37 |
| ---- | ---- |
| [Ubuntu py36 wheel](http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/nptsne-${version}-cp36-none-linux_x86_64.whl) | [Ubuntu py37 wheel](http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/nptsne-${version}-cp37-none-linux_x86_64.whl)|
