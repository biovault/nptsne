===========
Coding tips
===========

These are a series of tips for using the t-SNE and HSNE functionality. 
For complete documentation refer to the :doc:`nptsne API Reference <./nptsne>`. 


The code given in the tips is all taken from either the documentation examples 
(in the docstrings or see :doc:`nptsne API Reference <./nptsne>`)
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

Assuming *mnist* [#]_ is a dictionary containg numpy arrays the following code
will produce an embedding:

.. code-block:: python

    tsne = nptsne.TextureTsne(True)  # True triggers verbose output
    embed = tsne.fit_transform(mnist["data"])
    print(embed.shape)
    embed = embed.reshape(70000, 2)

.. [#] *mnist* in this example is the well known `handwritten digits data <http://yann.lecun.com/exdb/mnist/>`_.

1. Creating an extended t-SNE embedding
---------------------------------------

The class :py:class:`nptsne.TextureTsneExtended` add flexibility to the API in :py:class:`nptsne.TextureTsne`.
It permits running a number of iterations, examine the embedding,
then running more embeddings. Force exaggeration decay (refer to the t-SNE GPU paper [NP2019]_)
can be triggered a suitable point.

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

HSNE is designed for visual analyis of large multidimensional data. An HSNE visual analytics session typically
follows a number of steps:

1. Create a multi-scale *HSNE* hierarchy
2. Display an embedding [#]_ based on all the landmarks [#]_ in the topmost scale
3. Interact with clusters in the embedding to make subselections of landmarks.

    a) Handle landmark selections by displaying the *Area of Interest*
    corresponding to the landmark (how this is done this is application dependent).

4. Choose a selection to create a lower scale analysis with :py:class:`nptsne.hsne_analysis.Analysis`
5. Display an embedding based on that *Analysis*. Continue with step 3.
6. Repeat steps 3., 4, and 5. to create a tree of analysis and corresponding visualizations.


.. [#] The examples use *t-SNE* embeddings
.. [#] An *HSNE* landmark at scale n is defined to be a datapoint representing a number of neighbouring (as defined by the chosen metric) points at scale n-1

Support for HSNE based visual analytics in nptsne
-------------------------------------------------

The submodule :py:mod:`nptsne.hsne_analysis` contains classes to assist in the creation
and navigation of a hierarchy of analyses:

- :py:class:`nptsne.hsne_analysis.Analysis` - a selection of landmarks at one *HSNE* scale under examination
- :py:class:`nptsne.hsne_analysis.AnalysisModel` - a hierarchy of landmark selections (:py:class:`nptsne.hsne_analysis.Analysis`) representing the totality of a visual analytics session
- :py:class:`nptsne.hsne_analysis.AnalysisContainer` - a container type used by `nptsne.hsne_analysis.AnalysisModel` to hold :py:class:`nptsne.hsne_analysis.Analysis`


The nptsne embedded support for visual analytics is limited to data management but examples of how visualization 
can be done (using matplotlib and PyQt5) can be found in the demos.
The :py:mod:`nptsne.hsne_analysis` system forms the core of both the |HSNEdemo_github_url| and the |EXHSNEdemo_github_url|.

A number of the steps have been highlight (in simplified form) here:

1. Create a multi-scale HSNE hierarchy
--------------------------------------

Code is adapted from |doctest_github_url| run_doctest.py.

.. code-block:: python

    import nptsne
    import numpy as np
    data = np.random.randint(256, size=(10000, 16)) # create some random data
    hsne = nptsne.HSne(True) # a verbose HSne object
    hsne.create_hsne(hsne_data, 3) # create a three level hierarchy
    # create the ctop level analysis using all the landmarks
    top_analysis = nptsne.hsne_analysis.Analysis(hsne, nptsne.hsne_analysis.EmbedderType.CPU)

2. Creating an analysis hierarchy
---------------------------------

This is a simplified overview showing one way to perform visual analytics with :py:class:`nptsne.HSne` 
and the :py:mod:`nptsne.hsne_analysis` support classes in python. See |HSNEdemo_github_url| for details.

2a. Display and iterate the analysis embedding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Code fragments are adapted from |HSNEdemo_github_url| AnalysisGui.py

Python library *matplotlib* supports interactive scatter plots and plot animation.
This can be used to display and iterate the t-SNE embedding of the - :py:class:`nptsne.hsne_analysis.Analysis`.
The actual code is more complex and includes selections and the display of the 
corresponding *mnist* digits on mouse over. In the actual AnalysisGui.py 
the code shown is part of a an *AnalysisGui* class 
permitting multiple analysis embeddings to be show simultaneously.

.. code-block:: python


    import matplotlib.pyplot as plt
    from nptsne import hsne_analysis
    # input_analysis could be top_analysis as shown above
    # or the result of a new selection
    analysis: hsne_analysis.Analysis = input_analysis
    fig = plt.figure(num=str(analysis))
    # setup animation
    ani = animation.FuncAnimation(
        fig,
        iterate_Tsne,
        init_func=self.start_plot,
        frames=range(self.num_frames),
        interval=100,
        repeat=True,
        blit=True,
    )
    stop_iter = False
    num_iters = 350

    def start_plot()
        # Reserve space for a scatter plot of the embedding,
        #
        # ***********************************************************
        embedding = self.analysis.embedding   # Extract the embedding
        # ***********************************************************
        x = embedding[:, 0]
        y = embedding[:, 1]
        # ********************************************************************
        scatter = ax.scatter( # Point size represents the landmark weight
            x, y, s=analysis.landmark_weights * 8, c="b", alpha=0.4, picker=10
        )
        # ********************************************************************

    def iterate_Tsne(i):
        # In practice do several iterations per animation frame
        # to give a smoother feeling to the embedding
        fig.canvas.flush_events()

        if not stop_iter:
            # *********************
            analysis.do_iteration()  # Perform an iteration of the embedding
            # *********************

            if i == num_iters:
                stop_iter = True

            # Update point positions
            # *************************************
            scatter.set_offsets(analysis.embedding) # Update the scatter plot
            # *************************************
            # At this point the embedding plot should be rescaled
            # as the size of the embedding changes.
            # See AnalysisGui.py update_scatter_plot_limits for details

2b. Select a region in the embedding to create a new analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Code fragments adapted from |HSNEdemo_github_url| AnalysisGui.py and ModelGui.py

The code concentrates on the conversion between a selection rectangle and 
the creation of the new analysis.

.. code-block:: python

    # The selection origin is tracked in the rorg_xy tuple (embedding coords)
    # The current cursor coordinate is dim_xy (embedding coords)
    def on_end_select(self, event):
        # ******************************
        if self.analysis.scale_id == 0:  # at the data level can't drill down
            return
        # ******************************

        # *********************************
        embedding = analysis.embedding  # Get the embedding points that fall in the current selection rectangle
        # *********************************
        # Get the ordered indexes at this analysis level 
        indexes = np.arange(embedding.shape[0])
        selected_indexes = indexes[
            (embedding[:, 0] > rorg_xy[0])
            & (embedding[:, 0] < rorg_xy[0] + dim_xy[0])
            & (embedding[:, 1] > rorg_xy[1])
            & (embedding[:, 1] < rorg_xy[1] + dim_xy[1])
        ]
        if selected_indexes.shape[0] > 0:
            # ************************************************************************
            new_analysis = analysis_model.add_new_analysis(analysis, selected_indexes) # Add a new analysis to the model with the current one as parent
            # ************************************************************************


3. Extending the *HSNE* viewers
-------------------------------

The |EXHSNEdemo_github_url|, a simple but fairly complete visual analysis tool, 
includes two additional viewers capable of visualizing other types of multidimensional data:

1. Image is datapoint - MNIST like data
2. Hyperspectral image - examples include hyperspectral image of sun and multispectral earth oberservation satellite imaging
3. Point and meta data - for example cell data classified according to gene expression and meta data related to cell types that can be used to color the embeddings


|EXHSNEdemo_github_url| extends the approach in |HSNEdemo_github_url|. The *AnalysisGui* has been
split into a reusable *EmbeddingGui* (for the analysis embedding) and separate viewers 
for the different data types: *HyperspectralImageViewer*,
*MetaDataViewer* and *CompositeImageViewer*. An *AnalysisController* mediates between selections and the manitenance
of the *AnalysisModel*.

A detailed explanation of these viewers and other support classes can be found in the |EXHSNEdemo_github_url| README.md

