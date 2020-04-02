#pragma once
#include <hdi/data/map_mem_eff.h>
#include <hdi/dimensionality_reduction/sparse_tsne_user_def_probabilities.h>
#include <hdi/dimensionality_reduction/hd_joint_probability_generator.h>
#include <hdi/dimensionality_reduction/gradient_descent_tsne_texture.h>
#include <hdi/data/embedding.h>

namespace nptsne{
    typedef float scalar_type;
    // a memory-efficient key => value map
    typedef hdi::data::MapMemEff<uint32_t,scalar_type> map_type;
    // use the memory-efficient map to hold sparse data 
    typedef std::vector<map_type> sparse_scalar_matrix_type;

    // a tSNE embedder that works with sparse data
    typedef hdi::dr::SparseTSNEUserDefProbabilities<scalar_type,sparse_scalar_matrix_type> sparse_tsne_type;
    
    // a tSNE embedder based on the OpenGL texture acceleration
    typedef hdi::dr::GradientDescentTSNETexture texture_tsne_type;

    // The embedding holder 
    typedef hdi::data::Embedding<scalar_type> embedding_type;   

    // The probability generator
    typedef hdi::dr::HDJointProbabilityGenerator<scalar_type> prob_gen_type;
}