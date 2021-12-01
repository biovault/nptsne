"""
        A numpy compatible python extension for GPGPU linear complexity tSNE and HSNE
        -----------------------------------------------------------------------------
    """
import nptsne.libs._nptsne
import typing
import enumKA
import enumKDM
import numpy
_Shape = typing.Tuple[int, ...]

__all__ = [
    "HSne",
    "HSneScale",
    "KnnAlgorithm",
    "KnnDistanceMetric",
    "TextureTsne",
    "TextureTsneExtended"
]


class HSne():
    """
            Initialize an HSne wrapper with logging state.

            Parameters
            ----------
            verbose : bool
                Enable verbose logging to standard output, default is False

            Examples
            --------
            Create an HSNE wrapper

            >>> import nptsne
            >>> hsne = nptsne.HSne(True)

            Attributes
            ----------
            num_data_points
            num_dimensions
            num_scales

            Notes
            -----
            HSne is a simple wrapper API for the Hierarchical SNE implementation.

            Hierarchical SNE is  is a GPU compute shader implementation of Hierarchical
            Stochastic Neighborhood Embedding described in [1]_.

            The wrapper can be
            used to create a new or load an existing hSNE analysis. The hSNE
            analysis is then held in the HSne instance and can be accessed through the
            class api.

            References
            ----------
            .. [1] `Hierarchical Stochastic Neighbor Embedding <https://doi.org/10.1111/cgf.12878>`_

            
    """
    def __init__(self, verbose: bool = False) -> None: ...
    @typing.overload
    def create_hsne(self, X: numpy.ndarray[numpy.float32], num_scales: int) -> bool: 
        """
                        Create the hSNE analysis data hierarchy with user assigned point ids from the input data with the number of scales required.

                        Parameters
                        ----------
                        X : :class:`ndarray`
                            The data used to create the saved file. Shape is : (num. data points, num. dimensions)

                        num_scales : int
                            How many scales to create in the hsne analysis

                        point_ids : :class:`ndarray`, optional
                            Array of ids associated with the data points

                        Examples
                        --------
                        >>> import nptsne
                        >>> hsne = nptsne.HSne(True)
                        >>> hsne.create_hsne(sample_hsne_data, 3)
                        True
                        >>> hsne.num_data_points
                        10000
                        >>> hsne.num_dimensions
                        16
                        >>> hsne.num_scales
                        3

                    
        """
    @typing.overload
    def create_hsne(self, X: numpy.ndarray[numpy.float32], num_scales: int, point_ids: numpy.ndarray[numpy.uint64]) -> bool: ...
    def get_scale(self, scale_number: int) -> HSneScale: 
        """
                    Get the scale information at the index. 0 is the HSNE data scale.

                    Parameters
                    ----------
                    scale_index : int
                        Index of the scale to retrieve

                    Examples
                    --------
                    The number of landmarks in scale 0 is the number of data points.

                    >>> scale = sample_hsne.get_scale(0)
                    >>> scale.num_points
                    10000

                    Returns
                    -------
                    :class:`HSneScale`
                        A numpy array contain a flatten (1D) embedding
                
        """
    def load_hsne(self, X: numpy.ndarray[numpy.float32], file_path: str) -> bool: 
        """
                        Load the HSNE analysis data hierarchy from a pre-existing HSNE file.

                        Parameters
                        ----------
                        X : :class:`ndarray`
                            The data used to create the saved file. Shape is : (num. data points, num. dimensions)
                        file_path : str
                            Path to saved HSNE file

                        Examples
                        --------
                        Load hsne from a file, and check that is contains the expected data

                        >>> import nptsne
                        >>> import doctest
                        >>> loaded_hsne = nptsne.HSne(True)
                        >>> loaded_hsne.load_hsne(sample_hsne_data, sample_hsne_file)  # doctest: +ELLIPSIS
                        True
                        >>> loaded_hsne.num_data_points
                        10000
                        >>> loaded_hsne.num_dimensions
                        16
                        >>> loaded_hsne.num_scales
                        3

                    
        """
    @staticmethod
    def read_num_scales(file_path: str) -> int: 
        """
                    Read the number of scales defined in stored hSNE data without fully loading the file.

                    Parameters
                    ----------
                    filename : str
                        The path to a saved hSNE

                    Examples
                    --------
                    Read the number of scales from a saved file

                    >>> import nptsne
                    >>> nptsne.HSne.read_num_scales(sample_hsne_file)
                    3

                    Returns
                    -------
                    int
                        The number of scales in the saved hierarchy

                
        """
    def save(self, file_path: str) -> None: 
        """
                    Save the HSNE as a binary structure to a file

                    Parameters
                    ----------
                    filename : str
                        The file to save to. If it already exists it is overwritten.

                    Examples
                    --------
                    Save the hsne to a file and check the number of scales was saved correctly.

                    >>> import nptsne
                    >>> from pathlib import Path
                    >>> from tempfile import gettempdir
                    >>> savepath = Path(gettempdir(), "save_test.hsne")
                    >>> sample_hsne.save(str(savepath))
                    >>> nptsne.HSne.read_num_scales(str(savepath))
                    3

                
        """
    @property
    def num_data_points(self) -> int:
        """
                    int: The number of data points in the HSne.

                    Examples
                    --------

                    >>> sample_hsne.num_data_points
                    10000
                

        :type: int
        """
    @property
    def num_dimensions(self) -> int:
        """
                    int: The number of dimensions associated with the original data.

                    Examples
                    --------

                    >>> sample_hsne.num_dimensions
                    16
                

        :type: int
        """
    @property
    def num_scales(self) -> int:
        """
                    int: The number of scales in the HSne.

                    Examples
                    --------

                    >>> sample_hsne.num_scales
                    3
                

        :type: int
        """
    pass
class HSneScale():
    """
            Create a wrapper for the HSNE data scale. The function :func:`HSne.get_scale` works more directly than
            calling the constructor on this class.

            Parameters
            ----------
            hsne : :class:`HSne`
                The hierarchical SNE being explored
            scale_number : int
                The scale from the nsne to wrap

            Examples
            --------
            Using the initializer to create an HSneScale wrapper.
            Scale 0 contains the datapoints.  (Prefer the HSne.get_scale function)

            >>> import nptsne
            >>> scale = nptsne.HSneScale(sample_hsne, 0)
            >>> scale.num_points
            10000

            Attributes
            ----------
            num_points
            transition_matrix
            landmark_orig_indexes
            
    """
    def __init__(self, hsne: HSne, scale_number: int) -> None: ...
    def get_landmark_weight(self) -> numpy.ndarray[numpy.float32]: 
        """
                    The weights per landmark in the scale.

                    Examples
                    --------
                    The size of landmark weights should match the number of points

                    >>> num_points = sample_scale2.num_points
                    >>> weights = sample_scale2.get_landmark_weight()
                    >>> weights.shape[0] == num_points
                    True

                    All weights at scale 0 should be 1.0

                    >>> weights = sample_scale0.get_landmark_weight()
                    >>> test = weights[0] == 1.0
                    >>> test.all()
                    True

                    Returns
                    -------
                    :class:`ndarray`
                        Weights array in landmark index order

                
        """
    @property
    def area_of_influence(self) -> typing.List[typing.List[typing.Tuple[int, float]]]:
        """
                    The area of influence matrix in this scale.

                    Examples
                    --------
                    The size of landmark area of influence should match the number of points
                    in the more detailed (s-1) scale.

                    >>> len(sample_scale2.area_of_influence) == sample_scale1.num_points
                    True

                    Loop over all the landmarks, i, at scale 1.
                    Sum the influences from each landmark j at scale 2 on 
                    the individual landmarks i in scale 1.
                    For each landmark i at scale 1 the total influence from the j
                    landmarks should be approximately 1.0.
                    In this random data test the difference is assumed 
                    to be < :math:`1.5\mathrm{e}{-2}`.

                    >>> aoi_2on1 = sample_scale2.area_of_influence
                    >>> scale1_sum = {}
                    >>> all_tots_are_1 = True
                    >>> for i in aoi_2on1:
                    ...     sum_inf = 0.0
                    ...     for j_tup in i:
                    ...         sum_inf += j_tup[1]
                    ...     if abs(1 - sum_inf) > 0.015:
                    ...         print(f"{1- sum_inf}")
                    ...         all_tots_are_1 = False
                    >>> all_tots_are_1 == True
                    True

                    Notes
                    -----
                    The return is in list-of-lists (LIL) format.
                    The list returned has one entry for each landmark point i at scale s-1,
                    :math: `\mathcal{L}_{i}^{s-1}`.
                    Each entry is a list of tuples at where each tuple contains an index
                    j for a landmark at scale s,   :math: `\mathcal{L}_{j}^{s}`
                    and a value :math: `\mathit{I}^{S}(i,j)` representing the probability that the 
                    landmark point i at scale s-1 is influenced by 
                    landmark j at scale s.

                    The resulting matrix is sparse.

                    Returns
                    -------
                    list(list(tuple)):
                        The area of influence matrix in this scale

                

        :type: typing.List[typing.List[typing.Tuple[int, float]]]
        """
    @property
    def landmark_orig_indexes(self) -> numpy.ndarray[numpy.uint32]:
        """
                    Original data indexes for each landmark in this scale.

                    Examples
                    --------
                    At scale 0 the landmarks are all the data points.

                    >>> sample_scale0.landmark_orig_indexes.shape
                    (10000,)
                    >>> sample_scale0.landmark_orig_indexes[0]
                    0
                    >>> sample_scale0.landmark_orig_indexes[9999]
                    9999

                    Returns
                    -------
                    :class:`ndarray`:
                        An ndarray of the original data indexes.
                

        :type: numpy.ndarray[numpy.uint32]
        """
    @property
    def num_points(self) -> int:
        """
                    int: The number of landmark points in this scale

                    Examples
                    --------

                    >>> sample_scale0.num_points
                    10000
                

        :type: int
        """
    @property
    def transition_matrix(self) -> typing.List[typing.List[typing.Tuple[int, float]]]:
        """
                    The transition (probability) matrix in this scale.

                    Examples
                    --------
                    The size of the transition matrix should match the number of points

                    >>> sample_scale0.num_points == len(sample_scale0.transition_matrix)
                    True
                    >>> sample_scale1.num_points == len(sample_scale1.transition_matrix)
                    True
                    >>> sample_scale2.num_points == len(sample_scale2.transition_matrix)
                    True

                    Notes
                    -----
                    The list returned has one entry for each landmark point, each entry is a list
                    The inner list contains tuples where the first item
                    is an integer landmark index in the scale and the second item
                    is the transition matrix value for the two points.

                    The resulting matrix is sparse in list-of-lists (LIL) form, one list per row
                    containing a list of (column number:value) tuples.

                    Returns
                    -------
                    list(list(tuple)):
                        The transition (probability) matrix in this scale in list-of-lists form

                

        :type: typing.List[typing.List[typing.Tuple[int, float]]]
        """
    pass
class KnnAlgorithm():
    """
                Enumeration used to select the knn algorithm used. Three possibilities are
                supported:

                `KnnAlgorithm.Flann`: Knn using FLANN - Fast Library for Approximate Nearest Neighbors
                `KnnAlgorithm.HNSW`: Knn using Hnswlib - fast approximate nearest neighbor search
                `KnnAlgorithm.Annoy`: Knn using Annoy - Spotify Approximate Nearest Neighbors Oh Yeah
            

    Members:

      Flann

      HNSW

      Annoy
    """
    def __and__(self, other: object) -> object: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __invert__(self) -> object: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __or__(self, other: object) -> object: ...
    def __rand__(self, other: object) -> object: ...
    def __repr__(self) -> str: ...
    def __ror__(self, other: object) -> object: ...
    def __rxor__(self, other: object) -> object: ...
    def __setstate__(self, state: int) -> None: ...
    def __xor__(self, other: object) -> object: ...
    def get_supported_metrics(self) -> typing.Dict[str, object]: 
        """
                    Get a dict containing KnnDistanceMetric values supported by the KnnAlgorithm.

                    Parameters
                    ----------
                    knn_lib : :class:`KnnAlgorithm`
                        The algorithm being queried.

                    Examples
                    --------
                    Each algorithm has different support. See the tests below.

                    >>> import nptsne
                    >>> support = nptsne.KnnAlgorithm.get_supported_metrics(nptsne.KnnAlgorithm.Flann)
                    >>> for i in support.items():
                    ...     print(i[0])
                    Euclidean
                    >>> support = nptsne.KnnAlgorithm.get_supported_metrics(nptsne.KnnAlgorithm.Annoy)
                    >>> for i in support.items():
                    ...     print(i[0])
                    Cosine
                    Dot
                    Euclidean
                    Manhattan
                    >>> support = nptsne.KnnAlgorithm.get_supported_metrics(nptsne.KnnAlgorithm.HNSW)
                    >>> for i in support.items():
                    ...     print(i[0])
                    Euclidean
                    Inner Product
                    >>> support["Euclidean"] is nptsne.KnnDistanceMetric.Euclidean
                    True

                    Returns
                    -------
                    :class:`ndarray`
                        A numpy array contain a flatten (1D) embedding
                
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    Annoy: nptsne.libs._nptsne.KnnAlgorithm # value = <KnnAlgorithm.Annoy: 1>
    Flann: nptsne.libs._nptsne.KnnAlgorithm # value = <KnnAlgorithm.Flann: -1>
    HNSW: nptsne.libs._nptsne.KnnAlgorithm # value = <KnnAlgorithm.HNSW: 0>
    __members__: dict # value = {'Flann': <KnnAlgorithm.Flann: -1>, 'HNSW': <KnnAlgorithm.HNSW: 0>, 'Annoy': <KnnAlgorithm.Annoy: 1>}
    pass
class KnnDistanceMetric():
    """
                Enumeration used to select the knn distance metric used. Five possibilities are
                supported:

                `KnnDistanceMetric.Euclidean`: Euclidean metric for all algorithms
                `KnnDistanceMetric.InnerProduct`: Inner Product metric for HNSW
                `KnnDistanceMetric.Cosine`: Cosine metric for Annoy
                `KnnDistanceMetric.Manhattan`: Manhattan metric for Annoy
                `KnnDistanceMetric.Hamming`: Hamming metric for Annoy, not supported
                `KnnDistanceMetric.Dot`: Dot metric for Annoy
            

    Members:

      Euclidean

      Cosine

      InnerProduct

      Manhattan

      Hamming

      Dot
    """
    def __and__(self, other: object) -> object: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __invert__(self) -> object: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __or__(self, other: object) -> object: ...
    def __rand__(self, other: object) -> object: ...
    def __repr__(self) -> str: ...
    def __ror__(self, other: object) -> object: ...
    def __rxor__(self, other: object) -> object: ...
    def __setstate__(self, state: int) -> None: ...
    def __xor__(self, other: object) -> object: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    Cosine: nptsne.libs._nptsne.KnnDistanceMetric # value = <KnnDistanceMetric.Cosine: 1>
    Dot: nptsne.libs._nptsne.KnnDistanceMetric # value = <KnnDistanceMetric.Dot: 5>
    Euclidean: nptsne.libs._nptsne.KnnDistanceMetric # value = <KnnDistanceMetric.Euclidean: 0>
    Hamming: nptsne.libs._nptsne.KnnDistanceMetric # value = <KnnDistanceMetric.Hamming: 4>
    InnerProduct: nptsne.libs._nptsne.KnnDistanceMetric # value = <KnnDistanceMetric.InnerProduct: 2>
    Manhattan: nptsne.libs._nptsne.KnnDistanceMetric # value = <KnnDistanceMetric.Manhattan: 3>
    __members__: dict # value = {'Euclidean': <KnnDistanceMetric.Euclidean: 0>, 'Cosine': <KnnDistanceMetric.Cosine: 1>, 'InnerProduct': <KnnDistanceMetric.InnerProduct: 2>, 'Manhattan': <KnnDistanceMetric.Manhattan: 3>, 'Hamming': <KnnDistanceMetric.Hamming: 4>, 'Dot': <KnnDistanceMetric.Dot: 5>}
    pass
class TextureTsne():
    """
                Create a wrapper class for the linear tSNE implementation.

                Parameters
                ----------
                verbose : bool
                    Enable verbose logging to standard output
                iterations : int
                    The number of iterations to perform. This must be at least 1000.
                num_target_dimensions : int
                    The number of dimensions for the output embedding. Default is 2.
                perplexity : int
                    The tSNE parameter that defines the neighborhood size. Usually between 10 and 30. Default is 30.
                exaggeration_iter : int
                    The iteration when force exaggeration starts to decay.
                knn_algorithm : :class:`KnnAlgorithm`
                    The knn algorithm used for the nearest neighbor calculation.
                    The default is `Flann` for less than 50 dimensions `HNSW` may be faster
                knn_metric : :class:`KnnDistanceMetric`
                    The knn distance metric used for the nearest neighbor calculation.
                    The default is `KnnDistanceMetric.Euclidean` the only supported metric for `Flann`

                Examples
                --------
                Create an TextureTsne wrapper

                >>> import nptsne
                >>> tsne = nptsne.TextureTsne(verbose=True, knn_algorithm=nptsne.KnnAlgorithm.Annoy)
                >>> tsne.verbose
                True
                >>> tsne.iterations
                1000
                >>> tsne.num_target_dimensions
                2
                >>> tsne.perplexity
                30
                >>> tsne.exaggeration_iter
                250
                >>> tsne.knn_algorithm == nptsne.KnnAlgorithm.Annoy
                True

                Notes
                -----
                TextureTsne is a GPU compute shader implementation of the gradient descent
                linear tSNE. If the system does not support OpenGL 4.3 an abover the implementation
                falls back to the a Texture rendering approach as described in [1]_.

                See Also
                --------
                TextureTsneExtended

                References
                ----------
                .. [1] Pezzotti, N., Thijssen, J., Mordvintsev, A., Höllt, T., Van Lew, B., 
                    Lelieveldt, B.P.F., Eisemann, E., Vilanova, A. 
                    `GPGPU Linear Complexity t-SNE Optimization <https://doi.org/10.1109/TVCG.2019.2934307>`_
                    IEEE Transactions on Visualization and Computer Graphics 26, 1172–1181

            
    """
    def __init__(self, verbose: bool = False, iterations: int = 1000, num_target_dimensions: int = 2, perplexity: int = 30, exaggeration_iter: int = 250, knn_algorithm: KnnAlgorithm = enumKA.Flan, knn_metric: KnnDistanceMetric = enumKDM.Euclidean) -> None: ...
    def fit_transform(self, X: numpy.ndarray[numpy.float32]) -> numpy.ndarray[numpy.float32]: 
        """
                    Fit X into an embedded space and return that transformed output.

                    Parameters
                    ----------
                    X : :class:`ndarray`
                        The input data with shape (num. data points, num. dimensions)

                    Examples
                    --------
                    An 2D embedding is returned in the form of a numpy array
                    [x0, y0, x1, y1, ...].

                    >>> import nptsne
                    >>> tsne = nptsne.TextureTsne()
                    >>> embedding = tsne.fit_transform(sample_tsne_data)  # doctest: +SKIP_IN_CI
                    >>> embedding.shape  # doctest: +SKIP_IN_CI
                    (4000,)
                    >>> import numpy  # doctest: +SKIP_IN_CI
                    >>> embedding.dtype == numpy.float32  # doctest: +SKIP_IN_CI
                    True

                    Returns
                    -------
                    :class:`ndarray`
                        A numpy array contain a flatten (1D) embedding
                
        """
    @property
    def exaggeration_iter(self) -> int:
        """
                    int: The iteration where attractive force exaggeration starts to decay, set at initialization.

                    Examples
                    --------

                    >>> sample_texture_tsne.exaggeration_iter
                    250

                    Notes
                    -----
                    The gradient of the cost function used to iteratively optimize the embedding points :math:`y_i`
                    is a sum of an attractive and repulsive force :math:`\frac{\delta C} {\delta y_i} = 4(\phi * F_i ^{attr} - F_i ^{rep})`
                    The iterations up to exaggeration_iter increase the :math:`F_i ^{attr}` term by the factor :math:`\phi`
                    which then decays to 1.

                

        :type: int
        """
    @property
    def iterations(self) -> int:
        """
                    int: The number of iterations, set at initialization.

                    Examples
                    --------

                    >>> sample_texture_tsne.iterations
                    1000
                

        :type: int
        """
    @property
    def knn_algorithm(self) -> KnnAlgorithm:
        """
                    int: The KnnAlgorithm value, set at initialization.

                    Examples
                    --------

                    >>> import nptsne
                    >>> sample_texture_tsne.knn_algorithm == nptsne.KnnAlgorithm.Flann
                    True
                

        :type: KnnAlgorithm
        """
    @property
    def knn_distance_metric(self) -> KnnDistanceMetric:
        """
                    int: KnnDistanceMetric value, set at initialization.

                    Examples
                    --------

                    >>> import nptsne
                    >>> sample_texture_tsne.knn_distance_metric == nptsne.KnnDistanceMetric.Euclidean
                    True
                

        :type: KnnDistanceMetric
        """
    @property
    def num_target_dimensions(self) -> int:
        """
                    int: The number of target dimensions, set at initialization.

                    Examples
                    --------

                    >>> sample_texture_tsne.num_target_dimensions
                    2
                

        :type: int
        """
    @property
    def perplexity(self) -> int:
        """
                    int: The tsne perplexity, set at initialization.

                    Examples
                    --------

                    >>> sample_texture_tsne.perplexity
                    30
                

        :type: int
        """
    @property
    def verbose(self) -> bool:
        """
                    bool: True if verbose logging is enabled. Set at initialization.

                    Examples
                    --------

                    >>> sample_texture_tsne.verbose
                    False
                

        :type: bool
        """
    pass
class TextureTsneExtended():
    """
                Create an extended functionality wrapper for the linear tSNE implementation.

                Parameters
                ----------
                verbose : bool
                    Enable verbose logging to standard output, default is False
                num_target_dimensions : int
                    The number of dimensions for the output embedding. Default is 2.
                perplexity : int
                    The tSNE parameter that defines the neighborhood size. Usually between 10 and 30. Default is 30.
                knn_algorithm : :class:`KnnAlgorithm`
                    The knn algorithm used for the nearest neighbor calculation. The default is 'Flann' for less than 50 dimensions 'HNSW' may be faster
                knn_metric : :class:`KnnDistanceMetric`
                    The knn distance metric used for the nearest neighbor calculation.
                    The default is `KnnDistanceMetric.Euclidean` the only supported metric for `Flann`

                Attributes
                ----------
                decay_started_at
                iteration_count

                Examples
                --------
                Create an TextureTsneExtended wrapper

                >>> import nptsne
                >>> tsne = nptsne.TextureTsneExtended(verbose=True, num_target_dimensions=2, perplexity=35, knn_algorithm=nptsne.KnnAlgorithm.Annoy)
                >>> tsne.verbose
                True
                >>> tsne.num_target_dimensions
                2
                >>> tsne.perplexity
                35
                >>> tsne.knn_algorithm == nptsne.KnnAlgorithm.Annoy
                True

                Notes
                -----
                `TextureTsneExtended` offers additional control over the exaggeration decay
                compares to `TextureTsne`. Additionally it supports inputting an initial embedding.
                Linear tSNE is described in [1]_.

                See Also
                --------
                TextureTsne

                References
                ----------
                .. [1] Pezzotti, N., Thijssen, J., Mordvintsev, A., Höllt, T., Van Lew, B., 
                    Lelieveldt, B.P.F., Eisemann, E., Vilanova, A. 
                    `GPGPU Linear Complexity t-SNE Optimization <https://doi.org/10.1109/TVCG.2019.2934307>`_
                    IEEE Transactions on Visualization and Computer Graphics 26, 1172–1181

            
    """
    def __init__(self, verbose: bool = False, num_target_dimensions: int = 2, perplexity: int = 30, knn_algorithm: KnnAlgorithm = enumKA.Flan, knn_metric: KnnDistanceMetric = enumKDM.Euclidean) -> None: ...
    def close(self) -> None: 
        """
                    Release GPU resources for the transform
                
        """
    def init_transform(self, X: numpy.ndarray[numpy.float32], initial_embedding: numpy.ndarray[numpy.float32] = array([], dtype=float32)) -> bool: 
        """
                    Initialize the transform with given data and optional initial embedding.
                    Fit X into an embedded space and return that transformed output.

                    Parameters
                    ----------
                    X : :class:`ndarray`
                        The input data with shape (num. data points, num. dimensions)
                    initial_embedding : :class:`ndarray`
                        An optional initial embedding. Shape should be (num data points, num output dimensions)

                    Returns
                    -------
                    bool
                        True if successful, False otherwise

                    Examples
                    --------
                    Create an TextureTsneExtended wrapper and initialize the data. This step performs the knn.

                    >>> import nptsne
                    >>> tsne = nptsne.TextureTsneExtended()
                    >>> tsne.init_transform(sample_tsne_data)
                    True

                
        """
    def reinitialize_transform(self, initial_embedding: numpy.ndarray[numpy.float32] = array([], dtype=float32)) -> None: 
        """
                    Fit X into an embedded space and return that transformed output.
                    Knn is not recomputed. If no initial_embedding is supplied the embedding
                    is re-randomized.

                    Parameters
                    ----------
                    initial_embedding : :class:`ndarray`
                        An optional initial embedding. Shape should be (num data points, num output dimensions)

                    Examples
                    --------
                    Create an TextureTsneExtended wrapper and initialize the data and run for 250 iterations.

                    >>> import nptsne
                    >>> tsne = nptsne.TextureTsneExtended()
                    >>> tsne.init_transform(sample_tsne_data)
                    True
                    >>> embedding = tsne.run_transform(iterations=100)    # doctest: +SKIP_IN_CI
                    >>> tsne.iteration_count    # doctest: +SKIP_IN_CI
                    100
                    >>> tsne.reinitialize_transform()    # doctest: +SKIP_IN_CI
                    >>> tsne.iteration_count    # doctest: +SKIP_IN_CI
                    0

                
        """
    def run_transform(self, verbose: bool = False, iterations: int = 1000) -> numpy.ndarray[numpy.float32]: 
        """
                    Run the transform gradient descent for a number of iterations
                    with the current settings for exaggeration.

                    Parameters
                    ----------
                    verbose : bool
                        Enable verbose logging to standard output.
                    iterations : int
                        The number of iterations to run.


                    Examples
                    --------
                    Create an TextureTsneExtended wrapper and initialize the data and run for 250 iterations.

                    >>> import nptsne
                    >>> tsne = nptsne.TextureTsneExtended()
                    >>> tsne.init_transform(sample_tsne_data)
                    True
                    >>> embedding = tsne.run_transform(iterations=250)    # doctest: +SKIP_IN_CI
                    >>> embedding.shape    # doctest: +SKIP_IN_CI
                    (4000,)
                    >>> tsne.iteration_count    # doctest: +SKIP_IN_CI
                    250

                    Returns
                    -------
                    :class:`ndarray`
                        A numpy array contain a flatten (1D) embedding.
                        Coordinates are arranged: x0, y0, x, y1, ...
                
        """
    def start_exaggeration_decay(self) -> None: 
        """
                    Enable exaggeration decay. Effective on next call to run_transform.
                    From this point exaggeration decays over the following 150 iterations,
                    the decay this is a fixed parameter.
                    This call is ony effective once.

                    Examples
                    --------
                    Starting decay exaggeration is recorded in the decay_started_at property.

                    >>> import nptsne
                    >>> tsne = nptsne.TextureTsneExtended()
                    >>> tsne.init_transform(sample_tsne_data)
                    True
                    >>> tsne.decay_started_at
                    -1
                    >>> embedding = tsne.run_transform(iterations=100)    # doctest: +SKIP_IN_CI
                    >>> tsne.start_exaggeration_decay()    # doctest: +SKIP_IN_CI
                    >>> tsne.decay_started_at    # doctest: +SKIP_IN_CI
                    100

                    Raises
                    ------
                    RuntimeError
                        If the decay is already active. This can be ignored.
                
        """
    @property
    def decay_started_at(self) -> int:
        """
                    int: The iteration number when exaggeration decay started.
                    Is -1 if exaggeration decay has not started.

                    Examples
                    --------
                    Starting decay exaggeration is recorded in the decay_started_at property.

                    >>> sample_texture_tsne_extended.decay_started_at
                    -1

                

        :type: int
        """
    @property
    def iteration_count(self) -> int:
        """
                    int: The number of completed iterations of tSNE gradient descent.

                    >>> sample_texture_tsne_extended.iteration_count
                    0
                

        :type: int
        """
    @property
    def knn_algorithm(self) -> KnnAlgorithm:
        """
                    int: The KnnAlgorithm value, set at initialization.

                    Examples
                    --------

                    >>> import nptsne
                    >>> sample_texture_tsne_extended.knn_algorithm == nptsne.KnnAlgorithm.Flann
                    True
                

        :type: KnnAlgorithm
        """
    @property
    def knn_distance_metric(self) -> KnnDistanceMetric:
        """
                    int: The KnnDistanceMetric value, set at initialization.

                    Examples
                    --------

                    >>> import nptsne
                    >>> sample_texture_tsne_extended.knn_distance_metric == nptsne.KnnDistanceMetric.Euclidean
                    True
                

        :type: KnnDistanceMetric
        """
    @property
    def num_target_dimensions(self) -> int:
        """
                    int: The number of target dimensions, set at initialization.

                    Examples
                    --------

                    >>> sample_texture_tsne_extended.num_target_dimensions
                    2
                

        :type: int
        """
    @property
    def perplexity(self) -> int:
        """
                    int: The tsne perplexity, set at initialization.

                    Examples
                    --------

                    >>> sample_texture_tsne_extended.perplexity
                    30
                

        :type: int
        """
    @property
    def verbose(self) -> bool:
        """
                    bool: True if verbose logging is enabled. Set at initialization.

                    Examples
                    --------

                    >>> sample_texture_tsne_extended.verbose
                    False
                

        :type: bool
        """
    pass
