from ..libs._nptsne._hsne_analysis import (EmbedderType, Analysis) 
import numpy as np

class AnalysisContainer:

    def __init__(self, top_analysis):
        self._container = {top_analysis.scale_id: {top_analysis.id: top_analysis}}
        self._children = {top_analysis.id: set()}
        self._scale_index = {top_analysis.id: top_analysis.scale_id}
        self._null_id = 0xffffffff
        
    def add_analysis(self, analysis):        
        if self._container.get(analysis.scale_id, None) is None: 
            self._container[analysis.scale_id] = {}
        self._container[analysis.scale_id][analysis.id] = analysis
        self._children[analysis.parent_id].add(analysis.id) 
        self._children[analysis.id] = set()
        self._scale_index[analysis.id] = analysis.scale_id
        
    def get_analysis(self, analysis_id):
        return self._container[self._scale_index[analysis_id]].get(analysis_id, None)
        
    def remove_analysis(self, analysis_id):
        """Removes analysis and (recursively) children
        
            return: list of analysis ids removed including this one
        """
        analysis = self.get_analysis(analysis_id)
        if analysis is None:
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
            result = result + "\nScale: " + str(key) + "\n";
            scale = self._container[key]
            skeys = list(scale.keys())
            skeys.sort()
            
            for skey in skeys:
                analysis = scale[skey]
                result = result + "\t" + str(analysis) + "\n";
        return result        
    
class AnalysisModel:
    """The hsne_analysis.AnalysisModel contains the user driven selections 
        when exploring an hsne hierarchy. The AnalysisModel is created
        with a top level default analysis containing all top level landmarks.."""
    
    def __init__(self, hsne, embedder_type):
        """Create an analysis model with the top level set up"""
        """Create a scale selection based
        
        Parameters
        ----------
        scale_id : HSne 
            The python HSne wrapper class
        """
        
        self.hsne = hsne
        self.embedder_type = embedder_type
        # The analyses are stored in a dict of dicts
        # where the outer dict represents the scales and
        # the inner (scale level) dicts are indexed by the unique
        # self-generated Analysis

        self._analysis_container = None
        # The uppermost scale id can be derived from the 
        # total number of scales
        self.top_scale_id = hsne.num_scales - 1
        # The lowest scale is always 0 - data level
        self.bottom_scale_id = 0
        self.top_analysis_id = None
        self._initialize_top_level()
    
    @property
    def top_analysis(self):
        "Get the top level analysis"
        return self._analysis_container.get_analysis(self.top_analysis_id)
        
    def _initialize_top_level(self):
        """The toplevel of the hsne_analysis.Model """
        
        # All the landmark points at from the top scale are in the 
        topAnalysis = Analysis(self.hsne, self.embedder_type) 
        self.top_analysis_id = topAnalysis.id
        self._analysis_container = AnalysisContainer(topAnalysis)
        
    def add_new_analysis(self, parent, parent_selection):
        """Add a new analysis based on a selection in a parent analysis
        
            Parameters
            ----------
            parent: Analysis
                The parent analysis
            
            parent_selection: ndarray<np.uint32>
                The selection indices in the parent analysis
                """

        analysis = Analysis(self.hsne, self.embedder_type, parent, parent_selection)
        self._analysis_container.add_analysis(analysis)
        return analysis
        
    def get_analysis(self, id):
        return self._analysis_container.get_analysis(id)
        
    @property
    def analysis_container(self):
        return self._analysis_container
    
    def get_landmark_indexes(self, parent_id, parent_selection):
        parent = self.analyses[parent_id]
        landmark_indexes = np.array((parent_selection.shape[0]), dtype=np.uintc)
        for i, idx in np.ndenumerate(parent_selection): 
            landmark_indexes[i] = parent.landmark_indexes[idx]
        return landmark_indexes   

    def remove_analysis(self, id):
        """Remove the analysis and all children
            return: list of deleted ids
        """
        return self._analysis_container.remove_analysis(id)
        
