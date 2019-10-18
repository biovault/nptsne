// Interface is a simplified version of https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
#include "TextureTsne.h"
#include "hdi/utils/cout_log.h"
#include "hdi/utils/log_helper_functions.h"
#include "hdi/data/embedding.h"
#include "hdi/data/panel_data.h"
#include "hdi/data/io.h"
#include "hdi/dimensionality_reduction/hd_joint_probability_generator.h"
#include "hdi/utils/scoped_timers.h"

#include <iostream>
#include <fstream>
#include <stdio.h>
#include <iostream>
#include <vector>

// not present in glfw 3.1.2
#ifndef GLFW_FALSE
#define GLFW_FALSE 0
#endif

// constructor
TextureTsne::TextureTsne(
	bool verbose, 
	int iterations, 
	int num_target_dimensions,
	int perplexity,
	int exaggeration_iter,
	KnnAlgorithm knn_algorithm
) : _verbose(verbose), _iterations(iterations), _num_target_dimensions(num_target_dimensions),
	_perplexity(perplexity), _exaggeration_iter(exaggeration_iter), _knn_algorithm(knn_algorithm), _offscreen_context(nullptr)
{
}
	
// tSNE transform and return results
// Only accept c-type float (row-major, dense) and cast any non conforming args. 
// Return a numpy compatible array.
//py::array_t<float, py::array::c_style>
py::array_t<float, py::array::c_style> TextureTsne::fit_transform(
	py::array_t<float, py::array::c_style | py::array::forcecast> X) 
{
	if (_verbose) {
		std::cout << "Iterations: " << _iterations << "\n";
		std::cout << "Target dimensions: " << _num_target_dimensions << "\n";
		std::cout << "Perplexity: " << _perplexity << "\n";
		std::cout << "Exaggeration iter.: " << _exaggeration_iter <<"\n";
		std::cout << "knn type: " << ((KnnAlgorithm::Flann == _knn_algorithm) ? "flann\n": "hnsw\n");
	}


	typedef float scalar_type;
    if (!glfwInit()) {
        throw std::runtime_error("Unable to initialize GLFW.");
    }
#ifdef __APPLE__ 
    glfwWindowHint (GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint (GLFW_CONTEXT_VERSION_MINOR, 1);
    glfwWindowHint (GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
    glfwWindowHint (GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);   
#endif    
    glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE); // invisible - ie offscreen, window
    _offscreen_context = glfwCreateWindow(640, 480, "", NULL, NULL);
    if (_offscreen_context == NULL)
    {
        glfwTerminate();
        throw std::runtime_error("Failed to create GLFW window");
    }
    glfwMakeContextCurrent(_offscreen_context);
    
    if (!gladLoadGLLoader((GLADloadproc) glfwGetProcAddress))
    {
        glfwTerminate();        
        throw std::runtime_error("Failed to initialize OpenGL context");
    }    

	auto result = py::array_t<float>(0);
	try {
		hdi::dr::GradientDescentTSNETexture tSNE;
		hdi::dr::HDJointProbabilityGenerator<scalar_type> prob_gen;
		hdi::dr::HDJointProbabilityGenerator<scalar_type>::sparse_scalar_matrix_type distributions;
		hdi::dr::HDJointProbabilityGenerator<scalar_type>::Parameters prob_gen_param;
		//hdi::dr::TsneParameters tSNE_param;
		hdi::data::Embedding<scalar_type> embedding;		
		auto X_loc = X;
		float similarities_comp_time = 0;
		float gradient_desc_comp_time = 0;
		py::buffer_info X_info = X_loc.request();
		if (X_info.ndim != 2) {
			throw std::runtime_error("Expecting input data to have two dimensions, data point and values");
		}
		_num_data_points = X_info.shape[0];
		_num_dimensions = X_info.shape[1];
		if (_verbose) {
			std::cout << "Read " << _num_data_points << " points,\n";
			std::cout << " and " << _num_dimensions << " value dimensions.\n";
		}

		hdi::utils::CoutLog log;
		{
			hdi::utils::ScopedTimer<float,hdi::utils::Seconds> timer(similarities_comp_time);
			prob_gen_param._perplexity = _perplexity;
			prob_gen_param._aknn_algorithm = static_cast<int>(_knn_algorithm);
			prob_gen.computeProbabilityDistributions(
				static_cast<float *>(X_info.ptr),
				_num_dimensions,
				_num_data_points,
				distributions,
				prob_gen_param);
		}

		std::cout << "knn complete" << "\n";

		std::cout << "grad descent tsne starting" << "\n";
		{
			hdi::utils::ScopedTimer<float,hdi::utils::Seconds> timer(gradient_desc_comp_time);
			tSNE_param._embedding_dimensionality = _num_target_dimensions;
			tSNE_param._mom_switching_iter = _exaggeration_iter;
			tSNE_param._remove_exaggeration_iter = _exaggeration_iter;
			tSNE.initialize(distributions,&embedding,tSNE_param);
			
			if (_verbose) {
				std::cout << "Computing gradient descent...\n";
			}
			for(int iter = 0; iter < _iterations; ++iter){
				tSNE.doAnIteration();
				if (_verbose) {
					std::cout << "Iter: " << iter << "\n";
				}
			}
			if (_verbose) {
				std::cout << "... done!\n";
			}
		}
		std::cout << "grad descent tsne complete" << "\n";
        glfwDestroyWindow(_offscreen_context);
        glfwTerminate();

		auto size = _num_data_points * _num_target_dimensions;
		result = py::array_t<float>(size);
		py::buffer_info result_info = result.request();
		float *output = static_cast<float *>(result_info.ptr);
		
		auto data = embedding.getContainer().data();
		for (decltype(size) i = 0; i < size; i++) {
			output[i] = data[i];
		}
		if (_verbose) {
			std::cout << "Similarities computation (sec) " << similarities_comp_time << "\n";
			std::cout << "Gradient descent (sec) " << gradient_desc_comp_time << "\n";
		}

	} 
	catch (const std::exception& e) {
		std::cout << "Fatal error: " << e.what() << std::endl;
	}
	return result;
	
}
