#include "TextureTsneExtended.h"
#include "hdi/dimensionality_reduction/tsne.h"
#include "hdi/utils/cout_log.h"
#include "hdi/utils/log_helper_functions.h"
#include "hdi/data/panel_data.h"
#include "hdi/data/io.h"
#include "hdi/utils/scoped_timers.h"

#include <iostream>
#include <fstream>
#include <stdio.h>
#include <iostream>
#include <vector>
#include <exception>

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
) : _verbose(verbose), _num_target_dimensions(num_target_dimensions),
	_perplexity(perplexity), _knn_algorithm(knn_algorithm), _offscreen_context(nullptr), _exaggeration_decay(false), _iteration_count(0), _have_preset_embedding(false)
{
}
	
// Initialise the tSNE with the data and an optional starting embedding
bool TextureTsneExtended::init_transform(
	py::array_t<float, py::array::c_style | py::array::forcecast> X,
	py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding) 
{
	auto embedding_loc = initial_embedding;
	py::buffer_info emb_info = embedding_loc.request();
	auto X_loc = X;
	py::buffer_info X_info = X_loc.request();
	if (X_info.ndim != 2) {
		throw std::runtime_error("Expecting input data to have two dimensions, data point and values");
	}
	_num_data_points = X_info.shape[0];
	_num_dimensions = X_info.shape[1];
	std::cout << "emb_info size: " <<  emb_info.size << " emb_info dims: " <<  emb_info.ndim << std::endl;
	if (emb_info.ndim == 2 && emb_info.size > 0) {
		if (_verbose) {
			std::cout << "Initialize from given embedding...\n";
			std::cout << "Embed dimensions: " << emb_info.shape[0] << ", " << emb_info.shape[1] << "\n";
		}
		_have_preset_embedding = true;
		float * emb_in = static_cast<float *>(emb_info.ptr);
		// user provided default for embedding - overwrite the random def.
		_embedding = hdi::data::Embedding<scalar_type>(emb_info.shape[0], emb_info.shape[1]);
		typename hdi::data::Embedding<scalar_type>::scalar_vector_type* embedding_container = &(_embedding.getContainer());
		// simply replace the container by the input?
		for(int p = 0; p < _num_data_points; p++) {
			for(int d = 0; d < 2; d++) {
				(*embedding_container)[p * 2 + d] = emb_in[p * 2 + d];
			}
		}
	}
	// std::cout << "Embedding size before init: " << _embedding.getContainer().size() << std::endl;
	if (_verbose) {
		std::cout << "Target dimensions: " << _num_target_dimensions << "\n";
		std::cout << "Perplexity: " << _perplexity << "\n";
		std::cout << "knn type: " << ((KnnAlgorithm::Flann == _knn_algorithm) ? "flann\n": "hnsw\n");
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
		hdi::dr::HDJointProbabilityGenerator<scalar_type> prob_gen;
		hdi::dr::HDJointProbabilityGenerator<scalar_type>::Parameters prob_gen_param;

		{
			hdi::utils::ScopedTimer<float,hdi::utils::Seconds> timer(similarities_comp_time);
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

void TextureTsneExtended::init_transform_with_distribution(nptsne::sparse_scalar_matrix_type& sparse_matrix)
{
    // use a default embedding
    _distributions = sparse_matrix;    
}

void TextureTsneExtended::start_exaggeration_decay() 
{
	if (!_exaggeration_decay) {
		hdi::dr::TsneParameters tSNE_param;
		_exaggeration_decay = true;
		tSNE_param._embedding_dimensionality = _num_target_dimensions;
		tSNE_param._mom_switching_iter = _iteration_count;
		tSNE_param._remove_exaggeration_iter = _iteration_count;
		tSNE_param._presetEmbedding = _have_preset_embedding;
		_decay_started_at = _iteration_count;
		_tSNE.updateParams(tSNE_param);
	}
	else {
		throw std::runtime_error("Exaggeration decay is already active.");
	}
}

int TextureTsneExtended::get_decay_started_at()
{
	return _decay_started_at;
}

int TextureTsneExtended::get_iteration_count()
{
	return _iteration_count;
}

py::array_t<float, py::array::c_style> TextureTsneExtended::run_transform(
	bool verbose,
	int iterations) 
{
	_verbose = verbose;
	_iterations = iterations;
    // std::cout << "Embedding size before run_transform: " << _embedding.getContainer().size() << std::endl;

	try {

		int argc = 1;
		float gradient_desc_comp_time = 0;
	
		std::cout << "grad descent tsne starting" << "\n";
		{
			hdi::utils::ScopedTimer<float,hdi::utils::Seconds> timer(gradient_desc_comp_time);

			bool continuing = _tSNE.isInitialized();
			if (!continuing) {
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
                glfwWindowHint (GLFW_CONTEXT_VERSION_MAJOR, 4);
                glfwWindowHint (GLFW_CONTEXT_VERSION_MINOR, 1);
                glfwWindowHint (GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
                glfwWindowHint (GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);   
#endif                  
                glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE); // inisible - ie offscreen, window
                _offscreen_context = glfwCreateWindow(640, 480, "", NULL, NULL);
                glfwMakeContextCurrent(_offscreen_context);

                if (!gladLoadGLLoader((GLADloadproc) glfwGetProcAddress))
                {
                    throw std::runtime_error("Failed to initialize OpenGL context");
                } 				
				std::cout << "initializing tSNE" << "\n";
				_tSNE.initialize(_distributions,&_embedding,tSNE_param);
			}
			else {
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
				std::cout << "continuing tSNE" << "\n";	
			}
			
			if (_have_preset_embedding) {
				if (_verbose) {
					std::cout << "Starting from given embedding...\n";
				}
			}
			else {
				if (_verbose) {
					if (!continuing) { 
						std::cout << "Starting from random embedding...\n";
					} 
					else {
						std::cout << "Continue previous embedding...\n";
					}
				}				
			}
			
			if (_verbose) {
				std::cout << "Continuing gradient descent from iteration: " << _iteration_count << "\n";
				if (_exaggeration_decay ) {
					std::cout << "Exaggeration state on \n";
				}
				else {
					std::cout << "Exaggeration decay started at iteration: " << _decay_started_at << "\n";
				}
			}
			
			for(int iter = 0; iter < _iterations; ++iter){
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
		//_tSNE.getEmbedding();
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

void TextureTsneExtended::reinitialize_transform(py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding)
{
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
            _embedding = hdi::data::Embedding<scalar_type>(emb_info.shape[0], emb_info.shape[1]);
            typename hdi::data::Embedding<scalar_type>::scalar_vector_type* embedding_container = &(_embedding.getContainer());
            // simply replace the container by the input?
            for(int p = 0; p < _num_data_points; p++) {
                for(int d = 0; d < 2; d++) {
                    (*embedding_container)[p * 2 + d] = emb_in[p * 2 + d];
                }
            }
        } 
        else {
            // No user supplied embedding clear the current one.
            // std::cout << "Embedding size before clear: " << _embedding.getContainer().size() << std::endl;
            _embedding = hdi::data::Embedding<scalar_type>();
            // std::cout << "Embedding size after clear: " << _embedding.getContainer().size() << std::endl;            
        }
        hdi::dr::TsneParameters tSNE_param;
        tSNE_param._embedding_dimensionality = _num_target_dimensions;
        tSNE_param._mom_switching_iter = 0;
        tSNE_param._remove_exaggeration_iter = 0;
        tSNE_param._presetEmbedding = _have_preset_embedding;    
        _tSNE.initialize(_distributions,&_embedding,tSNE_param);    
    } catch (std::exception& e) {
        std::cout << e.what() << std::endl;
        throw;
    }
}
    
void TextureTsneExtended::close() 
{
    glfwDestroyWindow(_offscreen_context);
    glfwTerminate();
    _offscreen_context = nullptr;
}
