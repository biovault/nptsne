// Copyright 2020 LKEB at LUMC
// Author: B. van Lew
#pragma once
#include <hdi/data/map_mem_eff.h>
#include <hdi/dimensionality_reduction/sparse_tsne_user_def_probabilities.h>
#include <hdi/dimensionality_reduction/hd_joint_probability_generator.h>
#include <hdi/dimensionality_reduction/gradient_descent_tsne_texture.h>
#include <hdi/dimensionality_reduction/hierarchical_sne.h>
#include <hdi/data/embedding.h>
#include <vector>

namespace nptsne {
    using ScalarType = float;

    using UnsignedIntType = uint32_t;

    // a memory-efficient key => value map
    using MapType = hdi::data::MapMemEff<uint32_t, ScalarType>;

    // The memory type of the MapMemEff
    using MapStorageType = MapType::storage_type;

    // use the memory-efficient map to hold sparse data
    using SparseScalarMatrixType = std::vector<MapType>;

    // a tSNE embedder that works with sparse data
    using SparseTsneType = hdi::dr::SparseTSNEUserDefProbabilities<ScalarType, SparseScalarMatrixType>;

    // a tSNE embedder based on the OpenGL texture acceleration
    using TextureTsneType = hdi::dr::GradientDescentTSNETexture;

    // The embedding holder
    using EmbeddingType = hdi::data::Embedding<ScalarType>;

    // The probability generator
    using ProbGenType = hdi::dr::HDJointProbabilityGenerator<ScalarType>;

    using HsneType = hdi::dr::HierarchicalSNE<float, SparseScalarMatrixType>;

    using DataPointID = std::uint64_t;

    // Data points...
    using PointIdContainerType = std::vector<DataPointID>;

    // ... are represented by landmarks ...
    using LandmarkContainerType = std::vector<PointIdContainerType>;

    // ... are contained at a different scales
    using ScalesContainerType = std::vector<LandmarkContainerType>;
}  // namespace nptsne
