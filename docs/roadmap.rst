Roadmap
======= 

The following items are envisioned for future releases:

1. Release a *manylinux* wheel on PyPi for full Linux support
2. Investigate adding a context manager for TextureTsneExtended to automatically close the nptsne OpenGL context. This would enable the following code:

.. code-block:: python
    :caption: Possible context manager for TextureTsneExtended

    with nptsne.TextureTsneExtended(False) as tsne:    
        tsne.init_transform(mnist['data'])
        embedding = tsne.run_transform(verbose=False, iterations=step_size)
    
    # TextureTsneExtended & OpenGL context have been freed at end of indent context
    # tsne.close() is not required.
    # Continue processing embedding result in parent context. e.g.:
    xyembed = embedding.reshape((70000, 2))
    plt.scatter(xyembed[..., 0], xyembed[..., 1])
    
    