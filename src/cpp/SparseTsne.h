// Copyright 2020 LKEB at LUMC
// Author: B. van Lew
#pragma once

// Class is a pared down version of N Pezzotti's MultiscaleEmbedderSingleView
// only the sparse tSNE embedder remains.

#include <hdi/dimensionality_reduction/sparse_tsne_user_def_probabilities.h>
#include <hdi/utils/cout_log.h>
#include <hdi/utils/abstract_log.h>
#include <hdi/data/map_mem_eff.h>
#include "Types.h"
#include <vector>

// Provides a wrapping for a sparse tSNE embedder
// The embedder can be initialized and per iteration the
// intermediate embedding can be retrieved.
class SparseTsne final {
 public:
    SparseTsne() : _logger(nullptr) {}
    // No virtual destructor - we are final

    void initialize(nptsne::SparseScalarMatrixType& sparse_matrix,
        uint32_t analysis_id,
        hdi::dr::TsneParameters params = hdi::dr::TsneParameters());

    void doAnIteration();

    nptsne::EmbeddingType& getEmbedding() { return _embedding; }

    nptsne::SparseScalarMatrixType& getTransitionMatrix() { return _sparse_matrix; }

    void setLogger(hdi::utils::AbstractLog* logger) {
        _logger = logger;
        _tSNE.setLogger(logger);
    }

 private:
    nptsne::SparseTsneType _tSNE;
    nptsne::EmbeddingType _embedding;
    nptsne::SparseScalarMatrixType _sparse_matrix;
    hdi::utils::AbstractLog* _logger;
    uint32_t _analysis_id;
};
