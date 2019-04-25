// Simplified version of https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
#include "TextureTsneExtended.h"
#include "hdi/dimensionality_reduction/tsne.h"
#include "hdi/utils/cout_log.h"
#include "hdi/utils/log_helper_functions.h"
#include "hdi/data/embedding.h"
#include "hdi/data/panel_data.h"
#include "hdi/data/io.h"
#include "hdi/dimensionality_reduction/hd_joint_probability_generator.h"
#include "hdi/dimensionality_reduction/gradient_descent_tsne_texture.h"
#include "hdi/utils/visual_utils.h"
#include "hdi/utils/scoped_timers.h"

#include <QtCore>
#include <QMetaObject>
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <iostream>
#include <vector>

// constructor
TextureTsneExtended::TextureTsneExtended(
	bool verbose, 
	int num_target_dimensions,
	int perplexity,
	int knn_algorithm
) : _verbose(verbose), _num_target_dimensions(num_target_dimensions),
	_perplexity(perplexity), _knn_algorithm(knn_algorithm)
{
}
	
// tSNE transform and return results
// Only accept c-type float (row-major, dense) and cast any non conforming args. 
// Return a numpy compatible array.
//py::array_t<float, py::array::c_style>
bool TextureTsneExtended::init_transform(
	py::array_t<float, py::array::c_style | py::array::forcecast> X) 
{
	if (_verbose) {
		std::cout << "Iterations: " << _iterations << "\n";
		std::cout << "Target dimensions: " << _num_target_dimensions << "\n";
		std::cout << "Perplexity: " << _perplexity << "\n";
		std::cout << "Exaggeration iter.: " << _exaggeration_iter <<"\n";
		std::cout << "knn type: " << ((-1 == _knn_algorithm) ? "flann\n": "hnsw\n");
	}
	try {

		auto X_loc = X;
		float similarities_comp_time = 0;

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
		hdi::dr::HDJointProbabilityGenerator<scalar_type> prob_gen;
		hdi::dr::HDJointProbabilityGenerator<scalar_type>::Parameters prob_gen_param;

		{
			hdi::utils::ScopedTimer<float,hdi::utils::Seconds> timer(similarities_comp_time);
			prob_gen_param._perplexity = _perplexity;
			prob_gen_param._aknn_algorithm = _knn_algorithm;
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


py::array_t<float, py::array::c_style> TextureTsneExtended::run_transform(
	bool verbose,
	int iterations,
	int exaggeration,
	py::array_t<float, py::array::c_style | py::array::forcecast> given_embed) 
{
	_verbose = verbose;
	_iterations = iterations;
	_exaggeration_iter = exaggeration;
	try {
		QFileInfo libInfo = LibInfo::get_lib_info();
		//std::cout << "set library path with " << libInfo.absolutePath().toStdString() << std::endl;
		//
		QApplication::addLibraryPath(libInfo.absolutePath());
		char *dllPath = const_cast<char *>(libInfo.absolutePath().toStdString().c_str());
		int argc = 1;
		auto app = std::make_unique<QApplication>(argc, static_cast<char **>(&dllPath));
		float gradient_desc_comp_time = 0;
		
		app->setQuitOnLastWindowClosed(false);
		QApplication::setApplicationName("TextureTsne tSNE");
		QApplication::setApplicationVersion("0.0.3");
		
		OffscreenBuffer _offscreen;
		_offscreen.bindContext();
		auto embedding_loc = given_embed;
		py::buffer_info emb_info = embedding_loc.request();

		hdi::dr::GradientDescentTSNETexture tSNE;
		hdi::dr::TsneParameters tSNE_param;
		hdi::data::Embedding<scalar_type> embedding;
		std::cout << "grad descent tsne starting" << "\n";
		{
			hdi::utils::ScopedTimer<float,hdi::utils::Seconds> timer(gradient_desc_comp_time);
			tSNE_param._embedding_dimensionality = _num_target_dimensions;
			tSNE_param._mom_switching_iter = _exaggeration_iter;
			tSNE_param._remove_exaggeration_iter = _exaggeration_iter;
			tSNE.initialize(_distributions,&embedding,tSNE_param);
			if (emb_info.ndim == 2) {
				if (_verbose) {
					std::cout << "Starting from given embedding...\n";
				}
				float * emb_in = static_cast<float *>(emb_info.ptr);
				// user provided default for embedding - overwrite the random def.
				typename hdi::data::Embedding<scalar_type>::scalar_vector_type* embedding_container = &(embedding.getContainer());
				// simply replace the container by the input?
				for(int p = 0; p < _num_data_points; p++) {
					for(int d = 0; d < 2; d++) {
						(*embedding_container)[p * 2 + d] = emb_in[p * 2 + d];
					}
				}
			}
			else {
				if (_verbose) {
					std::cout << "Starting from random embedding...\n";
				}				
			}
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
		_offscreen.releaseContext();

		auto size = _num_data_points * _num_target_dimensions;
		auto result = py::array_t<float>(size);
		py::buffer_info result_info = result.request();
		float *output = static_cast<float *>(result_info.ptr);
		
		auto data = embedding.getContainer().data();
		for (decltype(size) i = 0; i < size; i++) {
			output[i] = data[i];
		}
		if (_verbose) {
			std::cout << "Gradient descent (sec) " << gradient_desc_comp_time << "\n";
		}
		QMetaObject::invokeMethod(app.get(), "quit", Qt::QueuedConnection);
		app->exec();
		return result;	
	} 
	catch (const std::exception& e) {
		std::cout << "Fatal error: " << e.what() << std::endl;
	}
	return py::array_t<float>(0);		
}
