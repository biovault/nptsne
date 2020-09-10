Purpose
=======
Demonstrate the GPU accelerated TextureTsneExtended class using 70000 MNIST 28x28 digits.

Install
=======

Unpack data (if needed

> python ../unpack_data

Install nptsne

> pip install nptsne

Run
===
> python test.py

Result
======
Runs the t-SNE in blocks of 100 iterations saving an image at the end of each 100 iterations. 
The exaggeration forces start to decay from iteration 1000. At that point the clusters are seen to expand

Example results are in the images textext_00.png to textext_19.png representing the states from iteration 100 
to iteration 2000. 