from ..libs._nptsne._hsne_analysis import Analysis 
import numpy as np

class AnalysisTree:
    """The hsne_analysis.AnalysisTree contains the user driven selections 
        when exploring an hsne hierarchy. The AnalysisTree is created
        with a top level default analysis containing all top level landmarks.."""
    
    def __init__(self, hsne):
        """Create an analysis model with the top level set up"""
        """Create a scale selection based
        
        Parameters
        ----------
        scale_id : HSne 
            The python HSne wrapper class
        """
        
        self.hsne = hsne
        # The analyses are stored in an list of dicts
        # where the list represents the levels and
        # the dicts are indexed by the unique self-generated AnalysisSelection id

        self.analyses = {}
        # The uppermost scale id can be derived from the 
        # total number of scales
        self.top_scale_id = hsne.num_scales - 1
        # The lowsest scale is always 0 - data level
        self.bottom_scale_id = 0
        self._initialize_top_level()
        self.top_analysis_id = 0
        
    def _initialize_top_level(self):
        """The toplevel of the hsne_analysis.Model """
        
        topscale = self.hsne.get_scale(self.top_scale_id)
        # All the points at from the top scale are in the 
        landmark_indexes = np.arange(topscale.num_points, dtype=np.uint32)
        topAnalysis = Analysis(
            self.hsne, 
            landmark_indexes) 
        self.top_analysis_id = topAnalysis.id
        self.analyses[topAnalysis.id] = topAnalysis
        
    def add_new_analysis(self, parent, parent_selection):
        """Add a new analysis based on a selection in a parent analysis
        
            Parameters
            ----------
            parent: Analysis
                The parent analysis
            
            parent_selection: ndarray<np.uint32>
                The selection indices in the parent analysis
                """
        
        # Need to get the landmark ids at the 
        # analysis = Analysis(
        #    parent.scale_id - 1,
        #    , # landmark (scale) indexes
        #    , # landmark weights
        #    parent, # parent analysis id 
        #    parent_selection # indices of the selection in parent embedding 
        #)
        self.analyses[analysis.id] = None
        
    def get_landmark_indexes(self, parent_id, parent_selection):
        parent = self.analyses[parent_id]
        landmark_indexes = np.array((parent_selection.shape[0]), dtype=np.uintc)
        for i, idx in np.ndenumerate(parent_selection): 
            landmark_indexes[i] = parent.landmark_indexes[idx]
        return landmark_indexes    
