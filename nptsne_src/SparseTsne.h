#pragma once

// Class is a pared down version of N Pezzotti's MultiscaleEmbedderSingleView
// only the sparse tSNE embedder remains.

#include <vector>
#include <hdi/dimensionality_reduction/sparse_tsne_user_def_probabilities.h>
#include <hdi/utils/cout_log.h>
#include <hdi/utils/abstract_log.h>
#include <hdi/data/map_mem_eff.h>
#include "Types.h"

// Provides a wrapping for a sparse tSNE embedder
// The embedder can be initialized and per iteration the 
// intermediate embedding can be retrieved.
class SparseTsne final {
public:
   
    SparseTsne() : _logger(nullptr) {};
    // No virtual destructor - we are final
    
    void initialize(nptsne::sparse_scalar_matrix_type& sparse_matrix, uint32_t analysis_id, hdi::dr::TsneParameters params = hdi::dr::TsneParameters());
    
    void doAnIteration();
    
    nptsne::embedding_type& getEmbedding() {return _embedding;}
    
    nptsne::sparse_scalar_matrix_type& get_sparse_matrix() {return _sparse_matrix;}
    
    void setLogger(hdi::utils::AbstractLog* logger){
        _logger = logger; 
        _tSNE.setLogger(logger);
    }

private:
    nptsne::sparse_tsne_type _tSNE;
    nptsne::embedding_type _embedding;
    nptsne::sparse_scalar_matrix_type _sparse_matrix;
    hdi::utils::AbstractLog* _logger;
    uint32_t _analysis_id;
};