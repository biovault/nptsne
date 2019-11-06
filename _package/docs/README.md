### nptsne - A numpy compatible python extension for GPGPU linear complexity tSNE

The nptsne package is designed to export a number of python classes that
wrap GPGPU linear complexity tSNE
implementations based on the following publications
[DOI: 10.1109/TVCG.2019.2934307](https://doi.org/10.1109/TVCG.2019.2934307) or the [arXiv preprint](https://arxiv.org/abs/1805.10817v2)

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
| [Ubuntu py36 wheel](http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/nptsne-1.0.0rc4-cp36-none-linux_x86_64.whl) | [Ubuntu py37 wheel](http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/nptsne-1.0.0rc4-cp37-none-linux_x86_64.whl)|
