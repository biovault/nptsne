#pragma once

#include <hdi/data/embedding.h>
#include "HSne.h"
#include "SparseTsne.h"
#include "TextureTsneExtended.h"
#include "EmbedderType.h"
#include <cstdint>
#include <memory>
#include <vector>
#include <string>

struct Analysis {
    // Analysis factory
    static std::unique_ptr<Analysis> make_analysis(
        HSne &hsne,
        EmbedderType embedderType = EmbedderType::CPU,
        Analysis *parent = nullptr,
        std::vector<uint32_t> parent_selection = std::vector<uint32_t>());

    static void get_parent_landmark_selection(const Analysis& newAnalysis,
        std::vector<uint32_t>& parent_landmark_selection);

    static void reset_id() {id_counter = 0;}

    explicit Analysis(bool verbose = false) : textureEmbedder(verbose), remove_exaggeration_iter(170) {
        this->id = Analysis::get_new_id();
    }

    std::string toString() {
        return "Analysis[id=" +
            std::to_string(id) + ", num points=" +
            std::to_string(landmark_indexes.size()) + ", scale=" +
            std::to_string(scale_id) + "]";
    }

    void initialize_embedding() {
        if (EmbedderType::CPU == embedderType) {
            embedder.initialize(
                hsne->scale(scale_id)._transition_matrix, id);
        } else {
            textureEmbedder.init_transform_with_distribution(hsne->scale(scale_id)._transition_matrix);
        }
    }

    void initialize_embedding(nptsne::SparseScalarMatrixType &new_transition_matrix) {
        if (EmbedderType::CPU == embedderType) {
            embedder.initialize(
                new_transition_matrix, id);
        } else {
            textureEmbedder.init_transform_with_distribution(new_transition_matrix);
        }
    }

    void doAnIteration() {
        if (EmbedderType::CPU == embedderType) {
            embedder.doAnIteration();
        } else {
            if (remove_exaggeration_iter == textureEmbedder.get_iteration_count() + 1) {
                textureEmbedder.start_exaggeration_decay();
            }
            textureEmbedder.run_transform(false, 1);
        }
    }

    nptsne::EmbeddingType& getEmbedding() {
        if (EmbedderType::CPU == embedderType) {
            return embedder.getEmbedding();
        }
        return textureEmbedder.getEmbedding();
    }

    nptsne::SparseScalarMatrixType& getTransitionMatrix() {
                if (EmbedderType::CPU == embedderType) {
            return embedder.getTransitionMatrix();
        }
        return textureEmbedder.getTransitionMatrix();
    }

    uint32_t id;
    uint32_t scale_id;
    std::vector<uint32_t> landmark_indexes;  // indexes of landmarks at this scale
    std::vector<unsigned int> landmarks_orig_data;
    std::vector<float> landmark_weights;
    Analysis *parent;  // a selection the parent Analysis defined this analysis
    std::vector<uint32_t> parent_selection;  // indices of the selection within the parent analysis
    EmbedderType embedderType;
    SparseTsne embedder;
    TextureTsneExtended textureEmbedder;
    nptsne::HsneType *hsne;
    int remove_exaggeration_iter;

 private:
    static uint32_t get_new_id() {return id_counter++;}
    static uint32_t id_counter;
};

