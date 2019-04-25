#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
#include "LibInfo.h"
#include <tuple>
#include "OffscreenBuffer.h"
#include "hdi/dimensionality_reduction/hd_joint_probability_generator.h"

class TextureTsneExtended {
public:
	typedef float scalar_type;
	// constructor
	TextureTsneExtended(
		bool verbose=false,  
		int num_target_dimensions=2,
		int perplexity=30,
		int knn_algorithm=-1
		);
	// Initialize the probabilities based on the data
	bool init_transform(
		py::array_t<float, py::array::c_style | py::array::forcecast> X);
		
	py::array_t<float, py::array::c_style> run_transform(
		bool verbose=false,  
		int iterations=1000,
		int exaggeration_iter=250,			
		py::array_t<float, py::array::c_style | py::array::forcecast> embedding=py::array_t<scalar_type>({}));
	
private:

	hdi::dr::HDJointProbabilityGenerator<scalar_type>::sparse_scalar_matrix_type _distributions;
	int _num_data_points;
    int _num_dimensions;

    bool _verbose;
    int _iterations;
    int _exaggeration_iter;
    int _perplexity;
	int _knn_algorithm;
    double _theta;
    int _num_target_dimensions;
};