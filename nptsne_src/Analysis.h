#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <hdi/data/embedding.h>
#include "HSne.h"
#include "SparseTsne.h"
#include "TextureTsneExtended.h"

struct Analysis 
{ 
    enum class ActiveEmbedder{Sparse, Texture};
    
    // Analysis factory
    static std::unique_ptr<Analysis> make_analysis(
        HSne &hsne,
        Analysis *parent = nullptr,
        std::vector<uint32_t> parent_selection = std::vector<uint32_t>());

    static void get_parent_landmark_selection(const Analysis& newAnalysis, std::vector<uint32_t>& parent_landmark_selection);
    
    Analysis() {
        this->id = Analysis::get_new_id();
    }
    
    std::string toString() {
        return "Analysis[id=" + std::to_string(id) + ", num points=" + std::to_string(landmark_indexes.size()) + ", scale=" + std::to_string(scale_id) + "]"; 
    }
    
    void initialize_embedding() {
        if (ActiveEmbedder::Sparse == activeEmbedder) {
            embedder.initialize(
                hsne->scale(scale_id)._transition_matrix, id); 
        }
        textureEmbedder.init_transform_with_distribution(hsne->scale(scale_id)._transition_matrix);
    }
    
    void doAnIteration() {
        if (ActiveEmbedder::Sparse == activeEmbedder) {
            embedder.doAnIteration();
        }
        textureEmbedder.run_transform(false, 1);
    }
    
    nptsne::embedding_type& getEmbedding() {
        if (ActiveEmbedder::Sparse == activeEmbedder) {
            return embedder.getEmbedding();
        }
        return textureEmbedder.getEmbedding();
    }
    
    uint32_t id;
    uint32_t scale_id;
    std::vector<uint32_t> landmark_indexes; // indexes of landmarks at this scale
    std::vector<unsigned int> landmarks_orig_data;
    std::vector<float> landmark_weights;
    Analysis *parent; // a selection the parent Analysis defined this analysis 
    std::vector<uint32_t> parent_selection; //indices of the selection within the parent analysis 
    ActiveEmbedder activeEmbedder = ActiveEmbedder::Sparse;  
    SparseTsne embedder;
    TextureTsneExtended textureEmbedder;
    HSne::hsne_t *hsne;

private:
    static uint32_t get_new_id() {return id_counter++;}
    static uint32_t id_counter;
};

