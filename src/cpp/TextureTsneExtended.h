// Copyright 2020 LKEB at LUMC
// Author: B. van Lew
#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
#ifdef __APPLE__
    #include "glad/glad_3_3.h"
#endif
#include <GLFW/glfw3.h>
#include <tuple>
#include <hdi/dimensionality_reduction/knn_utils.h>
#include "hdi/data/embedding.h"
#include "hdi/dimensionality_reduction/hd_joint_probability_generator.h"
#ifdef __APPLE__
#define __gl3_h_
#endif
#include "hdi/dimensionality_reduction/gradient_descent_tsne_texture.h"

#include "Types.h"

class TextureTsneExtended {
 public:
    // constructor
    TextureTsneExtended(
        bool verbose = false,
        int num_target_dimensions = 2,
        int perplexity = 30,
        hdi::dr::knn_library knn_algorithm = hdi::dr::knn_library::KNN_FLANN,
        hdi::dr::knn_distance_metric knn_distance_metric = hdi::dr::knn_distance_metric::KNN_METRIC_EUCLIDEAN);

    // Initialize the probabilities based on the data
    bool init_transform(
        py::array_t<float, py::array::c_style | py::array::forcecast> X,
        py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding =
            py::array_t<nptsne::ScalarType>({}));

    void init_transform_with_distribution(nptsne::SparseScalarMatrixType& sparse_matrix);

    void start_exaggeration_decay();

    int get_decay_started_at();

    int get_iteration_count();

    bool get_verbose() { return _verbose; }
    int get_num_target_dimensions() { return _num_target_dimensions; }
    int get_iterations() { return _iterations; }
    int get_perplexity() { return _perplexity; }
    hdi::dr::knn_library get_knn_algorithm() { return _knn_algorithm; }

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
    int _iteration_count;
    bool _exaggeration_decay;
    int _decay_started_at;
    bool _verbose;
    int _iterations;
    int _perplexity;
    hdi::dr::knn_library _knn_algorithm;
    hdi::dr::knn_distance_metric _knn_metric;
    double _theta;
    int _num_target_dimensions;
    bool _have_preset_embedding;
    GLFWwindow* _offscreen_context;
};
