#include "Analysis.h"
#include <hdi/utils/graph_algorithms.h>

uint32_t Analysis::id_counter = 0;

// Factory method for analyses
Analysis Analysis::make_analysis(
    HSne &hsne,
    Analysis *parent,
    std::vector<uint32_t> parent_selection) 
{
    Analysis new_analysis = Analysis(); 
    new_analysis.scale_id = parent->scale_id - 1;
    new_analysis.parent = parent;
    new_analysis.parent_selection = parent_selection;
    new_analysis.hsne = hsne._hsne;
   
    // get the landmarks corresponsing to the parent selecton
    std::vector<uint32_t> parent_landmark_selection;
    Analysis::get_parent_landmark_selection(new_analysis, parent_landmark_selection);
    
    // From the parent level landmarks perform random walks to 
    // determine the  neighbouring landmarks at the previous scale 
    std::map<uint32_t, float> parent_neighbor_landmarks;
    new_analysis.hsne->getInfluencedLandmarksInPreviousScale(
        parent->scale_id, 
        parent_landmark_selection, 
        parent_neighbor_landmarks);
    
    // Use a 0.5 threshold to select relevant landmarks from those found
    std::vector<uint32_t> relevant_landmarks;
    for (auto l: parent_neighbor_landmarks) {
        if (l.second > 0.5) {
            relevant_landmarks.push_back(l.first);
        }
    }
    
    // Get a transition matrix and the landmark weights
    HSne::hsne_t::sparse_scalar_matrix_type new_transition_matrix;
    hdi::utils::extractSubGraph(
        new_analysis.hsne->scale(parent->scale_id)._transition_matrix,
        relevant_landmarks,
        new_transition_matrix,
        new_analysis.landmark_indexes,1);
        
    new_analysis.landmark_weights.reserve(new_analysis.landmark_indexes.size());
    for(auto id:  new_analysis.landmark_indexes){
        new_analysis.landmark_weights.push_back(
            new_analysis.hsne->scale(new_analysis.scale_id)._landmark_weight[id]);
    }  

    // Initialize the tSNE embedder with this selection to create a 2D embedding
    new_analysis.embedder.initialize(
        new_transition_matrix, new_analysis.id);
    
    return new_analysis;
}



void Analysis::get_parent_landmark_selection(const Analysis& newAnalysis, std::vector<uint32_t>& parent_landmark_selection)
{
    for(auto i :newAnalysis.parent_selection) {
        parent_landmark_selection.push_back(newAnalysis.parent->landmark_indexes[i]);
    }
}