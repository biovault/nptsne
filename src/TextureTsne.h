#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
#include "LibInfo.h"
#include "KnnAlgorithm.h"
#include "OffscreenBuffer.h"

class TextureTsne {
public:
	// constructor
	TextureTsne(
		bool verbose=false, 
		int iterations=1000, 
		int num_target_dimensions=2,
		int perplexity=30,
		int exaggeration_iter=250,
		KnnAlgorithm knn_algorithm=KnnAlgorithm::Flann
	);
		
	// tSNE transform and return results
	py::array_t<float, py::array::c_style> fit_transform(
		py::array_t<float, py::array::c_style | py::array::forcecast> X);
	
private:	
	int _num_data_points;
    int _num_dimensions;

    bool _verbose;
    int _iterations;
    int _exaggeration_iter;
    int _perplexity;
	KnnAlgorithm _knn_algorithm;
    double _theta;
    int _num_target_dimensions;
};