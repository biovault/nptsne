// Copyright 2020 LKEB at LUMC
// Author: B. van Lew
#include "TextureTsneExtended.h"
#include <cstdio>
#include <iostream>
#include <fstream>
#include <vector>
#include <exception>
#include "hdi/dimensionality_reduction/tsne.h"
#include "hdi/utils/cout_log.h"
#include "hdi/utils/log_helper_functions.h"
#include "hdi/data/panel_data.h"
#include "hdi/data/io.h"
#include "hdi/utils/scoped_timers.h"

// not present in glfw 3.1.2
#ifndef GLFW_FALSE
#define GLFW_FALSE 0
#endif
// constructor
TextureTsneExtended::TextureTsneExtended(
    bool verbose,
    int num_target_dimensions,
    int perplexity,
    KnnAlgorithm knn_algorithm
) : _verbose(verbose),
    _num_target_dimensions(num_target_dimensions),
    _perplexity(perplexity),
    _knn_algorithm(knn_algorithm),
    _offscreen_context(nullptr),
    _exaggeration_decay(false),
    _iteration_count(0),
    _have_preset_embedding(false) {
}

// Initialise the tSNE with the data and an optional starting embedding
bool TextureTsneExtended::init_transform(
    py::array_t<float, py::array::c_style | py::array::forcecast> X,
    py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding) {
    auto embedding_loc = initial_embedding;
    py::buffer_info emb_info = embedding_loc.request();
    auto X_loc = X;
    py::buffer_info X_info = X_loc.request();
    if (X_info.ndim != 2) {
        throw std::runtime_error("Expecting input data to have two dimensions, data point and values");
    }
    _num_data_points = X_info.shape[0];
    _num_dimensions = X_info.shape[1];
    std::cout << "emb_info size: " << emb_info.size << " emb_info dims: " << emb_info.ndim << std::endl;
    if (emb_info.ndim == 2 && emb_info.size > 0) {
        if (_verbose) {
            std::cout << "Initialize from given embedding...\n";
            std::cout << "Embed dimensions: " << emb_info.shape[0] << ", " << emb_info.shape[1] << "\n";
        }
        _have_preset_embedding = true;
        float * emb_in = static_cast<float *>(emb_info.ptr);
        // user provided default for embedding - overwrite the random def.
        _embedding = nptsne::EmbeddingType(emb_info.shape[0], emb_info.shape[1]);
        typename nptsne::EmbeddingType::scalar_vector_type* embedding_container = &(_embedding.getContainer());
        // simply replace the container by the input?
        for (int p = 0; p < _num_data_points; p++) {
            for (int d = 0; d < 2; d++) {
                (*embedding_container)[p * 2 + d] = emb_in[p * 2 + d];
            }
        }
    }
    // std::cout << "Embedding size before init: " << _embedding.getContainer().size() << std::endl;
    if (_verbose) {
        std::cout << "Target dimensions: " << _num_target_dimensions << "\n";
        std::cout << "Perplexity: " << _perplexity << "\n";
        std::cout << "knn type: " << ((KnnAlgorithm::Flann == _knn_algorithm) ? "flann\n" : "hnsw\n");
    }
    try {
        float similarities_comp_time = 0;
        _exaggeration_decay = false;
        _iteration_count = 0;
        _decay_started_at = -1;

        if (_verbose) {
            std::cout << "Read " << _num_data_points << " points,\n";
            std::cout << " and " << _num_dimensions << " value dimensions.\n";
        }

        hdi::utils::CoutLog log;
        nptsne::ProbGenType prob_gen;
        nptsne::ProbGenType::Parameters prob_gen_param;

        {
            hdi::utils::ScopedTimer<float, hdi::utils::Seconds> timer(similarities_comp_time);
            prob_gen_param._perplexity = _perplexity;
            prob_gen_param._aknn_algorithm = static_cast<hdi::utils::knn_library>(_knn_algorithm);
            prob_gen.computeProbabilityDistributions(
                static_cast<float *>(X_info.ptr),
                _num_dimensions,
                _num_data_points,
                _distributions,
                prob_gen_param);
        }

        std::cout << "knn complete" << "\n";
        if (_verbose) {
            std::cout << "Similarities computation (sec) " << similarities_comp_time << "\n";
        }
    }
    catch (const std::exception& e) {
        std::cout << "Fatal error: " << e.what() << std::endl;
        return false;
    }
    return true;
}

// Initialise the tSNE from a distance and an optional starting embedding
// No kNN are calculated but instead all data points are considered
bool TextureTsneExtended::init_transform_with_distance_matrix(
    py::array_t<float, py::array::c_style | py::array::forcecast> dist_mat,
    py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding)
{
    auto embedding_loc = initial_embedding;
    py::buffer_info emb_info = embedding_loc.request();
    auto dist_mat_loc = dist_mat;
    py::buffer_info dist_mat_info = dist_mat_loc.request();
    if (dist_mat_info.ndim != 2) {
        throw std::runtime_error("Expecting input data to have two dimensions, since it's a distance matrix");
    }
    if (dist_mat_info.shape[0] != dist_mat_info.shape[1]) {
        throw std::runtime_error("Expecting input distance matrix to be square");
    }
    _num_data_points = dist_mat_info.shape[0];
    std::cout << "emb_info size: " << emb_info.size << " emb_info dims: " << emb_info.ndim << std::endl;
    if (emb_info.ndim == 2 && emb_info.size > 0) {
        if (_verbose) {
            std::cout << "Initialize from given embedding...\n";
            std::cout << "Embed dimensions: " << emb_info.shape[0] << ", " << emb_info.shape[1] << "\n";
        }
        _have_preset_embedding = true;
        float * emb_in = static_cast<float *>(emb_info.ptr);
        // user provided default for embedding - overwrite the random def.
        _embedding = nptsne::EmbeddingType(emb_info.shape[0], emb_info.shape[1]);
        typename nptsne::EmbeddingType::scalar_vector_type* embedding_container = &(_embedding.getContainer());
        // simply replace the container by the input?
        for (int p = 0; p < _num_data_points; p++) {
            for (int d = 0; d < 2; d++) {
                (*embedding_container)[p * 2 + d] = emb_in[p * 2 + d];
            }
        }
    }
    // std::cout << "Embedding size before init: " << _embedding.getContainer().size() << std::endl;
    if (_verbose) {
        std::cout << "Target dimensions: " << _num_target_dimensions << "\n";
        std::cout << "Perplexity: " << _perplexity << "\n";
        std::cout << "Using all " << _num_data_points - 1 << "(number data points minus 1) data points as nearest neighbors.";
    }
    try {
        float similarities_comp_time = 0;
        _exaggeration_decay = false;
        _iteration_count = 0;
        _decay_started_at = -1;

        if (_verbose) {
            std::cout << "Read " << _num_data_points << " points,\n";
        }

        hdi::utils::CoutLog log;
        nptsne::ProbGenType prob_gen;
        nptsne::ProbGenType::Parameters prob_gen_param;

        {
            hdi::utils::ScopedTimer<float, hdi::utils::Seconds> timer(similarities_comp_time);
            prob_gen_param._perplexity = _perplexity;

            // Re-format values
            std::vector<float> distances_squared(static_cast<float *>(dist_mat_info.ptr), static_cast<float *>(dist_mat_info.ptr) + (_num_data_points*_num_data_points));
            prob_gen.computeProbabilityDistributionsFromDistanceMatrix(
                distances_squared,
                _num_data_points,
                _distributions,
                prob_gen_param);
        }

        std::cout << "High dimensional distribution calculation complete" << "\n";
        if (_verbose) {
            std::cout << "Similarities computation (sec) " << similarities_comp_time << "\n";
        }
    }
    catch (const std::exception& e) {
        std::cout << "Fatal error: " << e.what() << std::endl;
        return false;
    }
    return true;
}


// Initialise the tSNE from nearest neighbors
bool TextureTsneExtended::init_transform_with_kNN(
    py::array_t<float, py::array::c_style | py::array::forcecast> neighbor_dists,
    py::array_t<int, py::array::c_style | py::array::forcecast> neighbor_inds,
    py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding,
    bool allow_kNN_perplexity_mismatch)
{
    auto embedding_loc = initial_embedding;
    py::buffer_info emb_info = embedding_loc.request();
    auto neigh_dists_loc = neighbor_dists;
    py::buffer_info neigh_dists_info = neigh_dists_loc.request();
    auto neigh_inds_loc = neighbor_inds;
    py::buffer_info neigh_inds_info = neigh_inds_loc.request();
    if (neigh_dists_info.ndim != 2) {
        throw std::runtime_error("Expecting nieghbor data to have two dimensions, data points and the distances to their nearest neighbors");
    }
    if (neigh_dists_info.shape != neigh_inds_info.shape) {
        throw std::runtime_error("Expecting nieghbors distances and neighbor indices to have the same length");
    }
    if (neigh_dists_info.shape[1] != (_perplexity * 3 + 1)) {
        if (allow_kNN_perplexity_mismatch == true) {
            std::cout << "Potentially undesired behavior: kNN number does not match perplexity.\n";
        }
        else {
            throw std::runtime_error("Expecting neighbors distances and neighbor indices to have the same length");
        }
    }
    _num_data_points = neigh_dists_info.shape[0];
    _num_neighbors = neigh_dists_info.shape[1];
    std::cout << "emb_info size: " << emb_info.size << " emb_info dims: " << emb_info.ndim << std::endl;
    if (emb_info.ndim == 2 && emb_info.size > 0) {
        if (_verbose) {
            std::cout << "Initialize from given embedding...\n";
            std::cout << "Embed dimensions: " << emb_info.shape[0] << ", " << emb_info.shape[1] << "\n";
        }
        _have_preset_embedding = true;
        float * emb_in = static_cast<float *>(emb_info.ptr);
        // user provided default for embedding - overwrite the random def.
        _embedding = nptsne::EmbeddingType(emb_info.shape[0], emb_info.shape[1]);
        typename nptsne::EmbeddingType::scalar_vector_type* embedding_container = &(_embedding.getContainer());
        // simply replace the container by the input?
        for (int p = 0; p < _num_data_points; p++) {
            for (int d = 0; d < 2; d++) {
                (*embedding_container)[p * 2 + d] = emb_in[p * 2 + d];
            }
        }
    }
    // std::cout << "Embedding size before init: " << _embedding.getContainer().size() << std::endl;
    if (_verbose) {
        std::cout << "Target dimensions: " << _num_target_dimensions << "\n";
        std::cout << "Perplexity: " << _perplexity << "\n";
        std::cout << "kNN " << _num_neighbors - 1 << "\n";
    }
    try {
        float similarities_comp_time = 0;
        _exaggeration_decay = false;
        _iteration_count = 0;
        _decay_started_at = -1;

        if (_verbose) {
            std::cout << "Read " << _num_data_points << " points,\n";
        }

        hdi::utils::CoutLog log;
        nptsne::ProbGenType prob_gen;
        nptsne::ProbGenType::Parameters prob_gen_param;

        {
            hdi::utils::ScopedTimer<float, hdi::utils::Seconds> timer(similarities_comp_time);

            prob_gen_param._perplexity = _perplexity;

            // Re-format values
            std::vector<float> distances_squared(static_cast<float *>(neigh_dists_info.ptr), static_cast<float *>(neigh_dists_info.ptr) + (_num_data_points*_num_neighbors));
            std::vector<int> indices(static_cast<int *>(neigh_inds_info.ptr), static_cast<int *>(neigh_inds_info.ptr) + (_num_data_points*_num_neighbors));

            // This is ususally done in computeProbabilityDistributions()
            _distributions.resize(_num_data_points);

            // Use an overloaded, modified version of computeGaussianDistributions. Make sure to use a proper HDILib branch
            prob_gen.computeGaussianDistributions(distances_squared, indices, _num_neighbors, _distributions, prob_gen_param);
        }

        std::cout << "High dimensional distribution calculation complete" << "\n";
        if (_verbose) {
            std::cout << "Similarities computation (sec) " << similarities_comp_time << "\n";
        }
    }
    catch (const std::exception& e) {
        std::cout << "Fatal error: " << e.what() << std::endl;
        return false;
    }
    return true;
}

void TextureTsneExtended::init_transform_with_distribution(nptsne::SparseScalarMatrixType& sparse_matrix) {
    _num_data_points = sparse_matrix.size();
    _num_target_dimensions = 2;
    _distributions.clear();
    _embedding = nptsne::EmbeddingType(_num_target_dimensions, _num_data_points);
    // use a default embedding
    for (auto map : sparse_matrix) {
        _distributions.push_back(map);
    }
    if (_verbose) {
        std::cout << " Size of distribution " << _distributions.size() << "\n";
    }
}

void TextureTsneExtended::start_exaggeration_decay() {
    if (!_exaggeration_decay) {
        hdi::dr::TsneParameters tSNE_param;
        _exaggeration_decay = true;
        tSNE_param._embedding_dimensionality = _num_target_dimensions;
        tSNE_param._mom_switching_iter = _iteration_count;
        tSNE_param._remove_exaggeration_iter = _iteration_count;
        tSNE_param._presetEmbedding = _have_preset_embedding;
        _decay_started_at = _iteration_count;
        _tSNE.updateParams(tSNE_param);
    } else {
        throw std::runtime_error("Exaggeration decay is already active.");
    }
}

int TextureTsneExtended::get_decay_started_at() {
    return _decay_started_at;
}

int TextureTsneExtended::get_iteration_count() {
    return _iteration_count;
}

py::array_t<float, py::array::c_style> TextureTsneExtended::run_transform(
    bool verbose,
    int iterations) {
    _verbose = verbose;
    _iterations = iterations;
    // std::cout << "Embedding size before run_transform: " << _embedding.getContainer().size() << std::endl;

    try {
        int argc = 1;
        float gradient_desc_comp_time = 0;
        if (_verbose) {
            std::cout << "grad descent tsne starting" << "\n";
        }
        {
            hdi::utils::ScopedTimer<float, hdi::utils::Seconds> timer(gradient_desc_comp_time);

            bool continuing = _tSNE.isInitialized();
            if (!continuing) {
                if (_verbose) {
                    std::cout << "start a new tSNE" << "\n";
                }
                // a new tSNE
                hdi::dr::TsneParameters tSNE_param;
                tSNE_param._embedding_dimensionality = _num_target_dimensions;
                tSNE_param._mom_switching_iter = _iteration_count + iterations;
                tSNE_param._remove_exaggeration_iter = _iteration_count + iterations;
                tSNE_param._presetEmbedding = _have_preset_embedding;

                if (!glfwInit()) {
                    throw std::runtime_error("Unable to initialize GLFW.");
                }
#ifdef __APPLE__
                glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
                glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
                glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
                glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
#endif
                glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);  // invisible - ie offscreen, window
                _offscreen_context = glfwCreateWindow(640, 480, "", NULL, NULL);
                if (!_offscreen_context) {
                    throw std::runtime_error("Failed to create GLFW offscreen window");
                }
                glfwMakeContextCurrent(_offscreen_context);

                if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
                    throw std::runtime_error("Failed to initialize OpenGL context");
                }
                std::cout << "initializing tSNE" << "\n";
                _tSNE.initialize(_distributions, &_embedding, tSNE_param);
            } else {
                if (_verbose) {
                    std::cout << "continuing tSNE" << "\n";
                }
                // continuing tSNE possibly with new params from start_exaggeration_decay
                if (!_exaggeration_decay) {
                    // Continuing with no decay, maintain the disabled decay for this run
                    hdi::dr::TsneParameters tSNE_param;
                    tSNE_param._embedding_dimensionality = _num_target_dimensions;
                    tSNE_param._mom_switching_iter = _iteration_count + iterations;
                    tSNE_param._remove_exaggeration_iter = _iteration_count + iterations;
                    tSNE_param._presetEmbedding = _have_preset_embedding;
                    _tSNE.updateParams(tSNE_param);
                }
            }

            if (_have_preset_embedding) {
                if (_verbose) {
                    std::cout << "Starting from given embedding...\n";
                }
            } else {
                if (_verbose) {
                    if (!continuing) {
                        std::cout << "Starting from random embedding...\n";
                    } else {
                        std::cout << "Continue previous embedding...\n";
                    }
                }
            }

            if (_verbose) {
                std::cout << "Continuing gradient descent from iteration: " << _iteration_count << "\n";
                if (_exaggeration_decay) {
                    std::cout << "Exaggeration state on \n";
                } else {
                    std::cout << "Exaggeration decay started at iteration: " << _decay_started_at << "\n";
                }
            }

            for (int iter = 0; iter < _iterations; ++iter) {
                _tSNE.doAnIteration();
                if (_verbose) {
                    std::cout << "Iter: " << _iteration_count + iter << "\n";
                }
            }

            _iteration_count += _iterations;
            if (_verbose) {
                std::cout << " in total " << _iteration_count << " iterations done... \n";
            }
        }

        auto size = _num_data_points * _num_target_dimensions;
        auto result = py::array_t<float>(size);
        py::buffer_info result_info = result.request();
        float *output = static_cast<float *>(result_info.ptr);
        auto data = _embedding.getContainer().data();
        for (decltype(size) i = 0; i < size; i++) {
            output[i] = data[i];
        }
        if (_verbose) {
            std::cout << "Gradient descent (sec) " << gradient_desc_comp_time << "\n";
        }
        return result;
    }
    catch (const std::exception& e) {
        std::cout << "Fatal error: " << e.what() << std::endl;
    }
    return py::array_t<float>(0);
}

void TextureTsneExtended::reinitialize_transform(
    py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding) {
    if (!_tSNE.isInitialized()) {
        throw std::runtime_error("Tsne object must have been initialized in order to reinitialize.");
    }
    if (!_offscreen_context) {
        throw std::runtime_error("Tsne OpenGL context has been closed. Please reinitialize.");
    }
    _exaggeration_decay = false;
    _iteration_count = 0;
    _decay_started_at = -1;
    _have_preset_embedding = false;
    _iterations = 0;
    try {
        auto embedding_loc = initial_embedding;
        py::buffer_info emb_info = embedding_loc.request();
        if (emb_info.ndim == 2 && emb_info.size > 0) {
            if (_verbose) {
                std::cout << "Initialize from given embedding...\n";
                std::cout << "Embed dimensions: " << emb_info.shape[0] << ", " << emb_info.shape[1] << "\n";
            }
            _have_preset_embedding = true;
            float * emb_in = static_cast<float *>(emb_info.ptr);
            // user provided default for embedding - overwrite the random def.
            _embedding = nptsne::EmbeddingType(emb_info.shape[0], emb_info.shape[1]);
            typename nptsne::EmbeddingType::scalar_vector_type* embedding_container = &(_embedding.getContainer());
            // simply replace the container by the input?
            for (int p = 0; p < _num_data_points; p++) {
                for (int d = 0; d < 2; d++) {
                    (*embedding_container)[p * 2 + d] = emb_in[p * 2 + d];
                }
            }
        } else {
            // No user supplied embedding clear the current one.
            // std::cout << "Embedding size before clear: " << _embedding.getContainer().size() << std::endl;
            _embedding = nptsne::EmbeddingType();
            // std::cout << "Embedding size after clear: " << _embedding.getContainer().size() << std::endl;
        }
        hdi::dr::TsneParameters tSNE_param;
        tSNE_param._embedding_dimensionality = _num_target_dimensions;
        tSNE_param._mom_switching_iter = 0;
        tSNE_param._remove_exaggeration_iter = 0;
        tSNE_param._presetEmbedding = _have_preset_embedding;
        _tSNE.initialize(_distributions, &_embedding, tSNE_param);
    }
    catch (std::exception& e) {
        std::cout << e.what() << std::endl;
        throw;
    }
}

void TextureTsneExtended::close() {
    glfwDestroyWindow(_offscreen_context);
    glfwTerminate();
    _offscreen_context = nullptr;
}
