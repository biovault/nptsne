#pragma once

#include <cstdint>
#include <vector>
#include "HSne.h"
#include "SparseTsne.h"

struct Analysis 
{ 
    // Analysis factory
    static std::unique_ptr<Analysis> make_analysis(
        HSne &hsne,
        Analysis *parent,
        std::vector<uint32_t> parent_selection);

    static void get_parent_landmark_selection(const Analysis& newAnalysis, std::vector<uint32_t>& parent_landmark_selection);
    
    Analysis()
    {
        this->id = Analysis::get_new_id();
    }
    
    uint32_t id;
    uint32_t scale_id;
    std::vector<uint32_t> landmark_indexes; // indexes of landmarks at this scale
    std::vector<float> landmark_weights;
    Analysis *parent; // a selection the parent Analysis defined this analysis 
    std::vector<uint32_t> parent_selection; //indices of the selection within the parent analysis 
    SparseTsne embedder;
    HSne::hsne_t *hsne;

private:
    static uint32_t get_new_id() {return id_counter++;}
    static uint32_t id_counter;
};
