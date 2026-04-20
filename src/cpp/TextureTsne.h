// Copyright 2020 LKEB at LUMC
// Author: B. van Lew
#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>
namespace py = pybind11;
#ifndef __APPLE__
#include "glad/glad_3_3.h"
#endif
#include <GLFW/glfw3.h>
#include <hdi/dimensionality_reduction/knn_utils.h>
#include "hdi/dimensionality_reduction/tsne.h"
#ifdef __APPLE__
#define __gl3_h_
#include <OpenGL/gl3.h>
#endif
#include "hdi/dimensionality_reduction/gradient_descent_tsne_texture.h"
#include "Types.h"

class TextureTsne {
public:
    // constructor
    TextureTsne(
        bool verbose = false,
        int iterations = 1000,
        int num_target_dimensions = 2,
        int perplexity = 30,
        int exaggeration_iter = 250,
        hdi::dr::knn_library knn_algorithm = hdi::dr::knn_library::KNN_FLANN,
        hdi::dr::knn_distance_metric knn_distance_metric = hdi::dr::knn_distance_metric::KNN_METRIC_EUCLIDEAN,
        hdi::dr::GradientDescentTSNETexture::GpgpuSneType gpgpu_sne_type = hdi::dr::GradientDescentTSNETexture::GpgpuSneType::AUTO_DETECT);

    // tSNE transform and return results
    py::array_t<float, py::array::c_style> fit_transform(
        py::array_t<float, py::array::c_style | py::array::forcecast> X);

    bool get_verbose() { return _verbose; }
    int get_num_target_dimensions() { return _num_target_dimensions; }
    int get_iterations() { return _iterations; }
    int get_perplexity() { return _perplexity; }
    int get_exaggeration_iter() { return _exaggeration_iter; }
    std::vector<float>& get_kl_values() { return _kl_values; }
    hdi::dr::knn_library get_knn_algorithm() { return _knn_algorithm; }
    hdi::dr::knn_distance_metric get_knn_metric() { return _knn_metric; }
    nptsne::SparseScalarMatrixType& getTransitionMatrix() { return _distributions; }

private:
    int _num_data_points;
    int _num_dimensions;

    bool _verbose;
    int _iterations;
    int _exaggeration_iter;
    int _perplexity;
    std::vector<float> _kl_values;
    hdi::dr::knn_library _knn_algorithm;
    hdi::dr::knn_distance_metric _knn_metric;
    hdi::dr::GradientDescentTSNETexture::GpgpuSneType _gpgpu_sne_type;
    hdi::dr::TsneParameters tSNE_param;
    double _theta;
    int _num_target_dimensions;
    GLFWwindow* _offscreen_context;
    typename nptsne::SparseScalarMatrixType _distributions;
};

