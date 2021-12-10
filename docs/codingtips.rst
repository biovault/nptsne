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

The code shown is from |TTdemo_github_url| test.py and API is documented at at :py:class:`nptsne.TextureTsne`

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

The code shown here is adapted from |TTEdemo_github_url| testtextureextended.py and
the API is documented at :py:class:`nptsne.TextureTsneExtended`

.. code-block:: python

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

HSNE is designed for interactive visual exploration of large multidimensional data. This process
follows a number of steps:

1. Create a multi-scale HSNE hierarchy
2. Display an embedding [#]_ based on all the landmarks [#]_ in the topmost scale
3. Interact with clusters in the embedding to make subselections of landmarks.

    a) Handle landmark selections by displaying the *Area of Interest* 
    corresponding to the landmark (how this is done this is application dependent).

4. Choose a selection to create a lower scale analysis with :py:class:`nptse.hsne_analysis.Analysis`
5. Display an embedding based on that *Analysis*. Continue with step 3.
6. Repeat steps 3., 4, and 5. to create a tree of analysis and corresponding visualizations.


.. [#] The examples use t-SNE embeddings
.. [#] landmarks in an HSNE scale are the sub-set of datapoints represent all other points

This is the system behind bothe the |HSNEdemo_github_url| and |EXHSNEdemo_github_url|. 
A number of the steps have been highlight (in simplified form) here:

1. Create a multi-scale HSNE hierarchy
--------------------------------------

Code is adapted from |doctest_github_url| run_doctest.py and the |HSNEdemo_github_url|.

.. code-block:: python

    import nptsne
    import numpy as np
    data = np.random.randint(256, size=(10000, 16)) # create some random data
    hsne = nptsne.HSne(True) # a verbose HSne object
    hsne.create_hsne(hsne_data, 3) # create a three level hierarchy
    # create the ctop level analysis using all the landmarks
    top_analysis = nptsne.hsne_analysis.Analysis(hsne, nptsne.hsne_analysis.EmbedderType.CPU)

2. Displaying an analysis embedding hierarchy
---------------------------------------------


