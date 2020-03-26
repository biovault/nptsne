#include "Analysis.h"
#include <hdi/utils/graph_algorithms.h>
#include <iostream>

uint32_t Analysis::id_counter = 0;

// Factory method for analyses
std::unique_ptr<Analysis> Analysis::make_analysis(
    HSne &hsne,
    Analysis *parent,
    std::vector<uint32_t> parent_selection) 
{
    auto result = std::make_unique<Analysis>();

    result->parent = parent;
    result->parent_selection = parent_selection;
    result->hsne = hsne._hsne;
    
    if (nullptr == parent) {
        // making the toplevel analysis with
        // all toplevel landmarks
        std::cout << "Initialize num scales: "<< hsne.num_scales() << "\n";
        result->scale_id = hsne.num_scales() - 1;
        std::cout << "Get landmark weights\n";
        result->landmark_weights = hsne.get_scale(result->scale_id).getLandmarkWeight();
        std::cout << "Initialize embedder\n";
        std::cout << "Top scale transition matrix size: " << result->hsne->top_scale()._transition_matrix.size() << "\n";
        result->embedder.initialize(
            result->hsne->scale(result->scale_id)._transition_matrix, result->id);        
    }
    else {
        // A sub-analysis derived from a parent
        result->scale_id = parent->scale_id - 1;
        // get the landmarks corresponding to the parent selecton
        std::vector<uint32_t> parent_landmark_selection;
        Analysis::get_parent_landmark_selection(*result, parent_landmark_selection);
        
        // From the parent level landmarks perform random walks to 
        // determine the  neighbouring landmarks at the previous scale 
        std::map<uint32_t, float> parent_neighbor_landmarks;
        result->hsne->getInfluencedLandmarksInPreviousScale(
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
            result->hsne->scale(parent->scale_id)._transition_matrix,
            relevant_landmarks,
            new_transition_matrix,
            result->landmark_indexes,1);
            
        result->landmark_weights.reserve(result->landmark_indexes.size());
        for(auto id:  result->landmark_indexes){
            result->landmark_weights.push_back(
                result->hsne->scale(result->scale_id)._landmark_weight[id]);
        }  

        // Initialize the tSNE embedder with this selection to create a 2D embedding
        result->embedder.initialize(
            new_transition_matrix, result->id);
    }
    std::cout << "return new Analysis \n";
    return result;
}



void Analysis::get_parent_landmark_selection(const Analysis& newAnalysis, std::vector<uint32_t>& parent_landmark_selection)
{
    for(auto i :newAnalysis.parent_selection) {
        parent_landmark_selection.push_back(newAnalysis.parent->landmark_indexes[i]);
    }
}