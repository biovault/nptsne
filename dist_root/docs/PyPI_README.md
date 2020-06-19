### nptsne - A numpy compatible python extension for GPGPU linear complexity tSNE

The nptsne package is designed to export a number of python classes that
wrap GPGPU linear complexity tSNE or the hierarchical SNE (hSNE) method. 


When using nptsne please include the following citations when **using tSNE** and or **using hSNE**:

**using tSNE**

*Pezzotti, N., Thijssen, J., Mordvintsev, A., Höllt, T., Van Lew, B., Lelieveldt, B.P.F., Eisemann, E., Vilanova, A., (2020), "GPGPU Linear Complexity t-SNE Optimization" in IEEE Transactions on Visualization and Computer Graphics.\
doi: 10.1109/TVCG.2019.2934307\
keywords: {Minimization;Linear programming;Computational modeling;Approximation algorithms;Complexity theory;Optimization;Data visualization;High Dimensional Data;Dimensionality Reduction;Progressive Visual Analytics;Approximate Computation;GPGPU},\
URL: https://doi.org/10.1109/TVCG.2019.2934307 *

**using hSNE**

*Pezzotti, N., Höllt, T., Lelieveldt, B., Eisemann, E., Vilanova, A., (2016), "Hierarchical Stochastic Neighbor Embedding" in Computer Graphics Forum, 35: 21-30. \ 
doi:10.1111/cgf.12878\
keywords: {Categories and Subject Descriptors (according to ACM CCS), I.3.0 Computer Graphics: General},\
URL: https://doi.org/10.1111/cgf.12878 *

##### Attributions

The tSNE implementations are the original work of the authors named in the literature.

###### Full documentation

Full documentation is available at the [nptsne doc pages](https://biovault.github.io/nptsne/nptsne.html)


##### Linux support
Linux: (only Ubuntu 16.06 and upward is supported). Download the correct file (see below) for your python version and install using **pip install <file>.whl**

| py36 | py37 |
| ---- | ---- |
| [Ubuntu py36 wheel](http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/nptsne-${version}-cp36-none-linux_x86_64.whl) | [Ubuntu py37 wheel](http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/nptsne-${version}-cp37-none-linux_x86_64.whl)|
