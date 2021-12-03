"""Extension functionality for navigating HSNE analysis"""
import nptsne.libs._nptsne._hsne_analysis
import typing
import nptsne.libs._nptsne
import numpy
_Shape = typing.Tuple[int, ...]

__all__ = [
    "Analysis",
    "EmbedderType",
    "SparseTsne"
]


class Analysis():
    """
                Create a new analysis as a child of an (optional) parent analysis.

                Parameters
                ----------
                hsne : :class:`HSne`
                    The hierarchical SNE being explored
                embedder_type : :class:`EmbedderType`
                    The tSNE to use CPU or GPU based
                parent : :class:`Analysis`, optional
                    The parent Analysis (where the selection was performed) if any
                parent_selection : list, optional
                    List of selection indexes in the parent analysis.

                Attributes
                ----------
                number_of_points
                parent_id
                transition_matrix
                landmark_weights
                landmark_indexes
                landmark_orig_indexes
                embedding

                Examples
                --------
                The Analysis constructor is meant for use by the :class: `nptsne.hsne_analysis.AnalysisModel`.
                The example here illustrates how a top level analysis would be created from a sample hsne.

                >>> import nptsne
                >>> top_analysis = nptsne.hsne_analysis.Analysis(sample_hsne, nptsne.hsne_analysis.EmbedderType.CPU)
                >>> top_analysis.scale_id
                2
                >>> sample_hsne.get_scale(top_analysis.scale_id).num_points == top_analysis.number_of_points
                True

                Notes
                -----
                Together with `AnalysisModel` provides support for visual analytics of an hSNE.
                The Analysis class holds both the chosen landmarks at a particular
                scale but also permits referencing back to the original data.
                Additionally a t-SNE embedder is included (a choice is
                provided between GPU and CPU implementations) which can be used to create
                an embedding of the selected landmarks.

            
    """
    def __init__(self, hnse: nptsne.libs._nptsne.HSne, embedder_type: EmbedderType, parent: Analysis = None, parent_selection: typing.List[int] = []) -> None: ...
    def __str__(self) -> str: 
        """
                        str: A string summary of the analysis.

                        Examples
                        --------
                        >>> expected_str = 'Analysis[id={}, num points={}, scale={}]'.format(
                        ... sample_analysis.id, 
                        ... sample_analysis.number_of_points, 
                        ... sample_analysis.scale_id)
                        >>> str(sample_analysis) == expected_str
                        True
                    
        """
    def do_iteration(self) -> None: 
        """
        Perform one iteration of the chosen embedder
        """
    def get_area_of_influence(self, select_list: typing.List[int], threshold: float = 0.3) -> numpy.ndarray[numpy.float32]: 
        """
                        Get the area of influence of the selection in the original data.
                        For more information on the `threshold` refer to the HSNE paper
                        section *4.2 Filtering and drilling down*.

                        A fast but less accurate approach to obtaining area of influence 
                        is `get_mapped_area_of_influence`.

                        See Also
                        --------
                        get_mapped_area_of_influence

                        Parameters
                        ----------
                        select_list : list
                            A list of selection indexes for landmarks in this analysis
                        threshold: float, optional
                            The minimum value required for the underlying
                            datapoint to be considered in the landmark's region of influence.
                            Default is 0.3. The parameter must be in the range 0 to 1.0,
                            values outside the range it will be ignored.

                        Returns
                        -------
                        :class:`ndarray`
                            The indexes for the original points represented by the selected landmarks
                    
        """
    def get_mapped_area_of_influence(self, select_list: typing.List[int]) -> numpy.ndarray[numpy.uint32]: 
        """
                        Fast method to get the area of influence of the selection in the original data
                        based on non overlapping :math:`{1}\rightarrow{n}` mapping of scale landmarks
                        to original data points.

                        This mapping is derived by working bottom up from the data points and finding 
                        the landmarks at each scale with the maximum influence. The mapping is calculated
                        once on the first call to this function so subsequent calls are fast.

                        Due to thresholding it is possible that a datapoint may have no representative
                        landmark at a specific scale.

                        See Also
                        --------
                        get_area_of_influence

                        Parameters
                        ----------
                        select_list : list
                            A list of selection indexes for landmarks in this analysis

                        Examples
                        --------

                        Demonstrate the non-overlap of the area of influence for each landmark.

                        >>> import math
                        >>> import numpy as np
                        >>> all_top_landmarks=list(range(0,sample_analysis.number_of_points))
                        >>> all_influenced=sample_analysis.get_mapped_area_of_influence(all_top_landmarks)

                        Assumes that at least 99% of the datapoints are in the AOI of the
                        all toplevel landmarks.

                        >>> all_influenced.shape[0] > math.floor(sample_scale0.num_points * 0.99)
                        True

                        Concatenating the individual landmark AOIs

                        >>> infl_concat = np.empty((0,), dtype=np.uint32)
                        >>> for i in all_top_landmarks:
                        ...     influenced = sample_analysis.get_mapped_area_of_influence([i])
                        ...     infl_concat = np.concatenate([infl_concat, influenced])

                        Verify that all non-overlapping AOIs add to
                        the same size as the total AOI

                        >>> infl_concat.shape[0] == all_influenced.shape[0]
                        True

                        Concatenating the individual landmark AOIs gives the
                        same list of datapoints as all the landmarks AOI.

                        >>> all_influenced.sort()
                        >>> infl_concat.sort()
                        >>> (all_influenced == infl_concat).all()
                        True

                        Returns
                        -------
                        :class:`ndarray`
                            The indexes for the original points represented by the selected landmarks
                    
        """
    @property
    def embedding(self) -> numpy.ndarray[numpy.float32]:
        """
                    :class:`ndarray` : the tSNE embedding generated for this `Analysis`

                    Examples
                    --------
                    An embedding is a 2d float array. One entry per point.

                    >>> import numpy as np
                    >>> sample_analysis.embedding.shape == (sample_analysis.number_of_points, 2)
                    True
                    >>> sample_analysis.embedding.dtype == np.float32
                    True
                

        :type: numpy.ndarray[numpy.float32]
        """
    @property
    def id(self) -> int:
        """
                        int: Internally generated unique id for the analysis.

                        Examples
                        --------

                        >>> sample_analysis.id
                        0
                    

        :type: int
        """
    @id.setter
    def id(self, arg0: int) -> None:
        """
                        int: Internally generated unique id for the analysis.

                        Examples
                        --------

                        >>> sample_analysis.id
                        0
                    
        """
    @property
    def landmark_indexes(self) -> numpy.ndarray[numpy.uint32]:
        """
                    :class:`ndarray` : the indexes for the landmarks in this `Analysis`

                    Examples
                    --------
                    In a complete top level analysis all points are present
                    in this case all the points at scale2.

                    >>> import numpy as np
                    >>> np.array_equal(
                    ... np.arange(sample_scale2.num_points, dtype=np.uint32), 
                    ... sample_analysis.landmark_indexes)
                    True
                

        :type: numpy.ndarray[numpy.uint32]
        """
    @property
    def landmark_orig_indexes(self) -> numpy.ndarray[numpy.uint32]:
        """
                    :class:`ndarray` : the original data indexes for the landmarks in this `Analysis`

                    Examples
                    --------
                    The indexes are in the range of the original point indexes.

                    >>> import numpy as np
                    >>> np.logical_and(
                    ... sample_analysis.landmark_orig_indexes >= 0,
                    ... sample_analysis.landmark_orig_indexes < 10000).any()
                    True
                

        :type: numpy.ndarray[numpy.uint32]
        """
    @property
    def landmark_weights(self) -> numpy.ndarray[numpy.float32]:
        """
                    :class:`ndarray` : the weights for the landmarks in this `Analysis`

                    Examples
                    --------
                    There will be a weight for every point.

                    >>> weights = sample_analysis.landmark_weights
                    >>> weights.shape == (sample_analysis.number_of_points,)
                    True
                

        :type: numpy.ndarray[numpy.float32]
        """
    @property
    def number_of_points(self) -> int:
        """
                        int : number of landmarks in this `Analysis`

                        Examples
                        --------
                        The sample analysis is all the top scale points

                        >>> sample_analysis.number_of_points == sample_scale2.num_points
                        True
                    

        :type: int
        """
    @property
    def parent_id(self) -> int:
        """
        int : Unique id of the parent analysis

        :type: int
        """
    @property
    def scale_id(self) -> int:
        """
                        int: The number of this HSNE scale where this analysis is created.

                        Examples
                        --------
                        >>> sample_analysis.scale_id
                        2
                    

        :type: int
        """
    @scale_id.setter
    def scale_id(self, arg0: int) -> None:
        """
                        int: The number of this HSNE scale where this analysis is created.

                        Examples
                        --------
                        >>> sample_analysis.scale_id
                        2
                    
        """
    @property
    def transition_matrix(self) -> typing.List[typing.List[typing.Tuple[int, float]]]:
        """
        :type: typing.List[typing.List[typing.Tuple[int, float]]]
        """
    pass
class EmbedderType():
    """
                Enumeration used to select the embedder used. Two possibilities are
                supported:

                `EmbedderType.CPU`: CPU tSNE
                `EmbedderType.CPU`: GPU tSNE

            

    Members:

      CPU

      GPU
    """
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
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
    CPU: nptsne.libs._nptsne._hsne_analysis.EmbedderType # value = <EmbedderType.CPU: 0>
    GPU: nptsne.libs._nptsne._hsne_analysis.EmbedderType # value = <EmbedderType.GPU: 1>
    __members__: dict # value = {'CPU': <EmbedderType.CPU: 0>, 'GPU': <EmbedderType.GPU: 1>}
    pass
class SparseTsne():
    """
                SparseTsne a wrapper for an approximating tSNE CPU implementation as described in [1]_.

                Forms an alternative to `TextureTsne` when GPU acceleration for creation of the embedding
                is not available for internal use in the `Analysis` class

                Attributes
                ----------
                embedding : :class:`ndarray`

                See Also
                --------
                Analysis
                EmbedderType

                References
                ----------
                .. [1] Pezzotti, N., Lelieveldt, B.P.F., Maaten, L. van der, Höllt, T., Eisemann, E., Vilanova, A., 2017.
                    `Approximated and User Steerable tSNE for Progressive Visual Analytics. <https://doi.org/10.1109/TVCG.2016.2570755>`_
                    IEEE Transactions on Visualization and Computer Graphics 23, 1739–1752.
            
    """
    def do_iteration(self) -> None: 
        """
                    Perform a sinsle tSNE iteration on the sparse data.
                    Once complete the embedding coordinates can be read via the embedding property
                
        """
    @property
    def embedding(self) -> numpy.ndarray[numpy.float32]:
        """
        Embedding plot - shape embed dimensions x num points

        :type: numpy.ndarray[numpy.float32]
        """
    pass
__all__ = ('Analysis', 'SparseTsne', 'EmbedderType')
