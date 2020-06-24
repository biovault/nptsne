// Copyright 2020 LKEB at LUMC
// Author: B. van Lew
#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
#include "glad/glad.h"
#include <GLFW/glfw3.h>
#include <tuple>
#include "KnnAlgorithm.h"
#include "hdi/data/embedding.h"
#include "hdi/dimensionality_reduction/hd_joint_probability_generator.h"
#include "hdi/dimensionality_reduction/gradient_descent_tsne_texture.h"

#include "Types.h"

class TextureTsneExtended {
 public:
    // constructor
    TextureTsneExtended(
        bool verbose = false,
        int num_target_dimensions = 2,
        int perplexity = 30,
        KnnAlgorithm knn_algorithm = KnnAlgorithm::Flann);

    // Initialize the probabilities based on the data
    bool init_transform(
        py::array_t<float, py::array::c_style | py::array::forcecast> X,
        py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding =
            py::array_t<nptsne::ScalarType>({}));

    // Initialize the probabilities based on a distance matrix
    bool init_transform_with_distance_matrix(
        py::array_t<float, py::array::c_style | py::array::forcecast> dist_mat,
        py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding =
        py::array_t<nptsne::ScalarType>({}));

    // Initialize the probabilities based on a nearest neighbors 
    bool init_transform_with_kNN(
        py::array_t<float, py::array::c_style | py::array::forcecast> neighbor_dists,
        py::array_t<int, py::array::c_style | py::array::forcecast> neighbor_inds,
        py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding =
        py::array_t<nptsne::ScalarType>({}),
        bool allow_kNN_perplexity_mismatch = false);

    void init_transform_with_distribution(nptsne::SparseScalarMatrixType& sparse_matrix);

    void start_exaggeration_decay();

    int get_decay_started_at();

    int get_iteration_count();

    // Returns the recommended number of nearest neighbors based on perplexity
    int get_perplexity_matched_nn();
    
    py::array_t<float, py::array::c_style> run_transform(
        bool verbose = false,
        int iterations = 1000);

    // Restart the transform with an optional initial embedding
    void reinitialize_transform(
        py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding =
            py::array_t<nptsne::ScalarType>({}));

    void close();

    nptsne::EmbeddingType& getEmbedding() {return _embedding;}

    nptsne::SparseScalarMatrixType& getTransitionMatrix() {return _distributions;}

 private:
    typename nptsne::SparseScalarMatrixType _distributions;
    nptsne::EmbeddingType _embedding;
    hdi::dr::GradientDescentTSNETexture _tSNE;

    int _num_data_points;
    int _num_dimensions;
    int _num_neighbors;
    int _iteration_count;
    bool _exaggeration_decay;
    int _decay_started_at;
    bool _verbose;
    int _iterations;
    int _perplexity;
    KnnAlgorithm _knn_algorithm;
    double _theta;
    int _num_target_dimensions;
    bool _have_preset_embedding;
    GLFWwindow* _offscreen_context;
};
