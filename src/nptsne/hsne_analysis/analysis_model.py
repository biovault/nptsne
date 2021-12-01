import numpy as np

from ..libs._nptsne._hsne_analysis import Analysis, EmbedderType
from ..libs._nptsne import HSne
from typing import Set, Dict, List, Union


class AnalysisContainer:
    """A dict of dicts to store analyses

    Parameters
    ----------
    top_analysis: :class:`Analysis`
        The Analysis at the highest scale level containing all landmarks

    Notes
    -----
    The outer dict represents the scales and
    the inner dicts at scale level are indexed by the unique
    self-generated Analysis ids.
    """

    def __init__(self, top_analysis: Analysis):
        self._container: Dict[int, Dict[int, Analysis]] = {
            top_analysis.scale_id: {top_analysis.id: top_analysis}
        }
        self._children: Dict[int, Set] = {top_analysis.id: set()}
        self._scale_index: Dict[int, int] = {top_analysis.id: top_analysis.scale_id}
        self._null_id = 0xFFFFFFFF

    def __eq__(self, other):
        """To used for comparing an older copy with the current analysis container"""
        if not isinstance(other, AnalysisContainer):
            # don't attempt to compare against unrelated types
            return False

        if not other._scale_index == self._scale_index:
            return False

        for key, value in self._children:
            other_value = other._children[key]
            if not other_value == value:
                return False

        return True

    def add_analysis(self, analysis: Analysis) -> None:
        """Add a new analysis to the container

        Parameters
        ----------
        analysis : Analysis
            The new analysis
        """
        if self._container.get(analysis.scale_id, None) is None:
            self._container[analysis.scale_id] = {}
        self._container[analysis.scale_id][analysis.id] = analysis
        self._children[analysis.parent_id].add(analysis.id)
        self._children[analysis.id] = set()
        self._scale_index[analysis.id] = analysis.scale_id

    def get_analysis(self, analysis_id: int) -> Analysis:
        """Get the analysis corresponding to the id

        Parameters
        ----------
        analysis_id : int
            [description]

        Returns
        -------
        Analysis
            [description]

        Raises
        ------
        ValueError
            If the id does not correspond to an analysis
        """
        analysis = self._container[self._scale_index[analysis_id]].get(analysis_id, None)
        if analysis is None:
            raise ValueError("No analysis corresponding to the given id")

    def remove_analysis(self, analysis_id: int) -> List[int]:
        """Removes analysis and, recursively, child analyses

        Returns
        -------
        list[int]
            A list of analysis ids removed including this one
        """
        analysis = None
        try:
            analysis = self.get_analysis(analysis_id)
        except ValueError:
            return []
        removed_ids = [analysis.id]
        child_list = list(self._children[analysis.id])
        for id in child_list:
            removed_ids.append(id)
            removed_ids.extend(self.remove_analysis(id))
        # remove from the child tree
        del self._children[analysis.id]
        # and from the scale index lookup
        del self._scale_index[analysis.id]
        # remove the parent's children reference if any
        if not analysis.parent_id == self._null_id:
            self._children[analysis.parent_id].remove(analysis.id)
        # del the analysis reference in the analysis contaner
        del self._container[analysis.scale_id][analysis.id]
        print(f"removed: {analysis_id}")
        return removed_ids

    def __str__(self):
        keys = list(self._container.keys())
        # display is from top down
        keys.sort(reverse=True)
        result = ""
        for key in keys:
            result = result + "\nScale: " + str(key) + "\n"
            scale = self._container[key]
            skeys = list(scale.keys())
            skeys.sort()

            for skey in skeys:
                analysis = scale[skey]
                result = result + "\t" + str(analysis) + "\n"
        return result


class AnalysisModel:
    """Create an analysis model tree with the a top level Analysis containing all landmarks at the highest scale
    The AnalysisModel initially contains only the top analysis, i.e. the HSNE scale with the least number of points.
    As selections are made starting from the top analysis new sub analyses are added to the tree
    in AnalsisModel. The helper class AnalysisContainer is responsible for maintaining this tree of analyses.

    Parameters
    ----------
    hsne : HSne
        The python HSne wrapper class
    embedder_type : :class:`hsne_analysis.EmbedderType`
        The embedder to be used when creating a new analysis CPU or GPU

    Examples
    --------
    Initialize a model using loaded :class:`HSne` data.

    >>> import nptsne
    >>> model = nptsne.hsne_analysis.AnalysisModel(sample_hsne, nptsne.hsne_analysis.EmbedderType.CPU)
    >>> model.top_scale_id
    2

    Attributes
    ----------
    top_analysis
    analysis_container
    bottom_scale_id
    top_scale_id

    See Also
    --------
    hsne_analysis.Analysis
    hsne_analysis.EmbedderType.CPU

    Notes
    -----
    The hsne_analysis.AnalysisModel contains the user driven selections
    when exploring an HSNE hierarchy. The AnalysisModel is created
    with a top level default hsne_analysis.Analysis containing all top level landmarks.
    """

    def __init__(self, hsne: HSne, embedder_type: EmbedderType):
        self.hsne = hsne
        self.embedder_type = embedder_type

        self._analysis_container: AnalysisContainer
        # The uppermost scale id can be derived from the
        # total number of scales
        self.top_scale_id = hsne.num_scales - 1
        # The lowest scale is always 0 - data level
        self.bottom_scale_id = 0
        self.top_analysis_id: int
        self._initialize_top_level()

    @property
    def top_analysis(self) -> Analysis:
        """hsne_analysis.Analysis: The top level analysis

        Examples
        --------
        Retrieve the top level analysis containing all points at the top level.

        >>> import nptsne
        >>> model = nptsne.hsne_analysis.AnalysisModel(sample_hsne, nptsne.hsne_analysis.EmbedderType.CPU)
        >>> analysis = model.top_analysis
        >>> analysis.scale_id
        2

        Raises
        ------
        ValueError
            If there is not top analysis
        """
        return self._analysis_container.get_analysis(self.top_analysis_id)

    def _initialize_top_level(self):
        """The toplevel of the hsne_analysis.Model"""

        # All the landmark points at from the top scale are in the
        topAnalysis = Analysis(self.hsne, self.embedder_type)
        self.top_analysis_id = topAnalysis.id
        self._analysis_container = AnalysisContainer(topAnalysis)

    def add_new_analysis(self, parent: Analysis, parent_selection: np.ndarray) -> Analysis:
        """Add a new analysis based on a selection in a parent analysis

        Parameters
        ----------
        parent: Analysis
           The parent analysis

        parent_selection: ndarray<np.uint32>
           The selection indices in the parent analysis

        Examples
        --------
        Make a child analysis by selecting half of the points in the top analysis.
        The analysis is created at the next scale down is a child of the top level
        and contains an embedding of the right shape.

        >>> import nptsne
        >>> model = nptsne.hsne_analysis.AnalysisModel(sample_hsne, nptsne.hsne_analysis.EmbedderType.CPU)
        >>> sel = np.arange(int(model.top_analysis.number_of_points / 2))
        >>> analysis = model.add_new_analysis(model.top_analysis, sel)
        >>> analysis.scale_id
        1
        >>> analysis.parent_id == model.top_analysis.id
        True
        >>> analysis.embedding.shape == (analysis.number_of_points, 2)
        True
        """

        analysis = Analysis(self.hsne, self.embedder_type, parent, parent_selection)
        self._analysis_container.add_analysis(analysis)
        return analysis

    def get_analysis(self, id: int) -> Analysis:
        """Get the `Analysis` for the given id

        Parameters
        ----------
        id: int
           An Analysis id

        Examples
        --------
        >>> import nptsne
        >>> model = nptsne.hsne_analysis.AnalysisModel(sample_hsne, nptsne.hsne_analysis.EmbedderType.CPU)
        >>> id = model.top_analysis.id
        >>> str(model.top_analysis) == str(model.get_analysis(id))
        True

        Returns
        -------
            The Analysis corresponding to the id

        Raises
        ------
        ValueError
            If the id does not correspond to an analysis
        """

        return self._analysis_container.get_analysis(id)

    @property
    def analysis_container(self) -> AnalysisContainer:
        """The container for all analyses.

        This is an internal property exposed for debug purposes only"""
        return self._analysis_container

    def remove_analysis(self, id: int) -> List[int]:
        """Remove the analysis and all children

        Returns
        -------
        list[int]
            list of deleted ids

        Examples
        --------
        >>> import nptsne
        >>> model = nptsne.hsne_analysis.AnalysisModel(sample_hsne, nptsne.hsne_analysis.EmbedderType.CPU)
        >>> sel = np.arange(int(model.top_analysis.number_of_points / 2))
        >>> analysis = model.add_new_analysis(model.top_analysis, sel)
        >>> id = analysis.id
        >>> a_list = model.remove_analysis(analysis.id)
        >>> a_list == [id]
        """
        return self._analysis_container.remove_analysis(id)
