// Copyright 2020 LKEB at LUMC
// Author: B. van Lew
#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl_bind.h>
namespace py = pybind11;
#include "KnnAlgorithm.h"
#include <hdi/dimensionality_reduction/hierarchical_sne.h>
#include <hdi/utils/cout_log.h>
#include "Types.h"
#include <string>
#include <vector>

class HSneScale;
struct Analysis;

class HSne {
    friend Analysis;

 public:
    // constructor
    HSne(
        bool verbose = false);

    // provided two overloaded init_hsne functions
    // One without point ids (these default to 0 -> n-1)
    bool create_hsne(
        py::array_t<float, py::array::c_style | py::array::forcecast> X,
        int num_scales);

    bool create_hsne(
        py::array_t<float, py::array::c_style | py::array::forcecast> X,
        int num_scales,
        py::array_t<uint64_t, py::array::c_style | py::array::forcecast> point_ids);

    bool load_hsne(
        py::array_t<float, py::array::c_style | py::array::forcecast> X,
        const std::string &filePath);

    // save the raw hierarchy data to a file
    void save_to_file(const std::string &filePath);

    // Return scale info in a wrapper class
    HSneScale get_scale(unsigned int scale_number);

    // Check the version and read the number of scales from the hsne file 
    static int HSne::read_num_scales(const std::string &filePath);

    int num_scales() { return _num_scales; }
    int num_data_points() { return _num_data_points; }
    int num_dimensions() { return _num_dimensions; }

 private:
    int _num_scales;
    int _num_data_points;
    int _num_dimensions;
    int _num_target_dimensions;
    bool _verbose;
    int _seed;
    // The Hierarchical SNE algorithm
    nptsne::HsneType* _hsne;

    // Hold the user supplied or default point ids
    py::array_t<uint64_t, py::array::c_style | py::array::forcecast> *point_ids;

    nptsne::HsneType::Parameters _hsneParams;

    std::vector< std::vector<float>* > _landmarkWeights;

    // This container holds the landmarks created by HSNE
    nptsne::ScalesContainerType _derivedHierarchy;

    hdi::utils::CoutLog* _log;

    bool _init(
        py::array_t<float, py::array::c_style | py::array::forcecast> &X,
        uint64_t *point_ids,
        int num_point_ids,
        nptsne::SparseScalarMatrixType *top_scale_matrix = nullptr);

    void set_default_hsne_params();
};


class HSneScale {
    friend HSne;
 private:
    explicit HSneScale(nptsne::HsneType::scale_type scale) :
        _scale(scale) {
    }
 public:
    virtual ~HSneScale() {}

    // The length of the transition matrix is the number of points or landmarks
    int num_points() { return _scale._transition_matrix.size(); }

    nptsne::SparseScalarMatrixType& transition_matrix() { return _scale._transition_matrix; }

    nptsne::HsneType::scalar_vector_type getLandmarkWeight() {
        return _scale._landmark_weight;
    }

    nptsne::HsneType::scale_type _scale;
};

