===========
Coding tips
===========

These are a series of tips for using the t-SNE and HSNE functionality.

The code given in the tips is all taken from eithe the documentation examples (in the docstrings or see RTD)
or is available in the demos.

t-SNE tips
==========

1. Creating a simple t-SNE embedding
------------------------------------

The simple t-SNE class is called TextureTsne it uses either a GPU compute kernel (if available)
of a GPU texture driven approach to calculating t-SNE.

The code shown is from demos/TextureTsne/test.py and API at :py:meth:`nptsne.TextureTsne.__init__`

Note that the number of iterations or perplexity can be set when creating the `TextureTsne` object
but in the example the defaults are used.

Assuming *mnist* is a dictionary containg numpy arrays the following code
will produce an embedding:

.. code-block:: python

tsne = nptsne.TextureTsne(True)  # True triggers verbose output
embed = tsne.fit_transform(mnist["data"])
print(embed.shape)
embed = embed.reshape(70000, 2)



2. Creating an extended t-SNE embedding
---------------------------------------

The class TextureTsneExtended differs from TextureTsne in that
it is possible to run a number of iterations, examine the embedding,
then run more embeddings. Force exageration decay (refer to the t-SNE GPU paper)
can be set a suitable point.

The code shown is from demos/TextureTsneExtended/testtextureextended.py

.. code-block::python

tsne = nptsne.TextureTsneExtended(False)
tsne.init_transform(mnist["data"])

for i in range(20):
    # reduce the forces from iteration 1000
    if i == 10:
        tsne.start_exaggeration_decay()
    embedding = tsne.run_transform(verbose=False, iterations=100)
tsne.close()


HSNE tips
=========

T.B.D.



