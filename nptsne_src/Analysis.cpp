// Copyright 2020 LKEB at LUMC
// Author: B. van Lew
#include "Analysis.h"
#include <hdi/utils/graph_algorithms.h>
#include <iostream>
#include <memory>
#include <map>

uint32_t Analysis::id_counter = 0;

// Factory method for analyses
std::unique_ptr<Analysis> Analysis::make_analysis(
    HSne &hsne,
    EmbedderType embedderType,
    Analysis *parent,
    std::vector<uint32_t> parent_selection) {
    auto result = std::make_unique<Analysis>();

    result->parent = parent;
    result->parent_selection = parent_selection;
    result->hsne = hsne._hsne;
    result->embedderType = embedderType;
    if (nullptr == parent) {
        // making the toplevel analysis with
        // all toplevel landmarks
        std::cout << "Initialize num scales: "<< hsne.num_scales() << "\n";
        result->scale_id = hsne.num_scales() - 1;
        std::cout << "Get landmark weights\n";
        // all the landmarks in the scale are in the top level analysis
        result->landmark_weights = hsne.get_scale(result->scale_id).getLandmarkWeight();
        result->landmark_indexes.resize(result->landmark_weights.size());
        std::iota(result->landmark_indexes.begin(), result->landmark_indexes.end(), 0);
        std::cout << "Initialize embedder\n";
        std::cout << "Top scale transition matrix size: " <<
            result->hsne->top_scale()._transition_matrix.size() << "\n";
        result->initialize_embedding();
    } else {
        // A sub-analysis derived from a parent
        result->scale_id = parent->scale_id - 1;
        std::cout << "Sub-analysis at scale: " << result->scale_id << "\n";
        // get the landmarks corresponding to the parent selecton
        std::vector<uint32_t> parent_landmark_selection;
        Analysis::get_parent_landmark_selection(*result, parent_landmark_selection);

        std::cout << "Get the influence of these landmarks at the lower scale " << "\n";
        // From the parent level landmarks perform random walks to
        // determine the neighbouring landmarks at the previous scale
        std::map<uint32_t, float> parent_neighbor_landmarks;
        result->hsne->getInfluencedLandmarksInPreviousScale(
            parent->scale_id,
            parent_landmark_selection,
            parent_neighbor_landmarks);

        std::cout << "Filter landmarks with high relevance " << "\n";
        // Use a 0.5 threshold to select relevant landmarks from those found
        std::vector<uint32_t> relevant_landmarks;
        for (auto l : parent_neighbor_landmarks) {
            if (l.second > 0.5) {
                relevant_landmarks.push_back(l.first);
            }
        }

        // Get a transition matrix and the landmark weights
        std::cout << "Get the new transition matrix " << "\n";
        nptsne::SparseScalarMatrixType new_transition_matrix;
        hdi::utils::extractSubGraph(
            result->hsne->scale(result->scale_id)._transition_matrix,
            relevant_landmarks,
            new_transition_matrix,
            result->landmark_indexes, 1);

        result->landmark_weights.reserve(result->landmark_indexes.size());
        for (auto id : result->landmark_indexes) {
            result->landmark_weights.push_back(
                result->hsne->scale(result->scale_id)._landmark_weight[id]);
        }
        std::cout << "Initialize the embedder" << "\n";
        // Initialize the tSNE embedder with this selection to create a 2D embedding
        result->initialize_embedding(new_transition_matrix);
    }
    // Get the indexes for the original data
    for (auto& e : result->landmark_indexes) {
        result->landmarks_orig_data.push_back(
            result->hsne->scale(result->scale_id)._landmark_to_original_data_idx[e]);
    }
    std::cout << "return new Analysis \n";
    return result;
}

void Analysis::get_parent_landmark_selection(const Analysis& newAnalysis,
    std::vector<uint32_t>& parent_landmark_selection) {
    std::cout << "Get the landmark indexes of the parent selection \n";
    for (auto i : newAnalysis.parent_selection) {
        parent_landmark_selection.push_back(newAnalysis.parent->landmark_indexes[i]);
    }
}

