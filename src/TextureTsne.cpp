// Simplified version of https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
#include "TextureTsne.h"
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

#include <QApplication>
#include <QMetaObject>
#include <QFileInfo>
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <iostream>
#include <vector>

#if !defined(_WIN64) && !defined(_WIN32) 
#include <dlfcn.h>
QFileInfo get_lib_info() {
	Dl_info dlInfo;
	dladdr(reinterpret_cast<const void *>(QApplication::beep), &dlInfo);
	if (dlInfo.dli_sname != NULL && dlInfo.dli_saddr != NULL) {
		return QFileInfo(QString::fromLocal8Bit(dlInfo.dli_fname));
	}
	return QFileInfo("");
}

#else
EXTERN_C IMAGE_DOS_HEADER __ImageBase;

QFileInfo get_lib_info() {
	wchar_t fileName[MAX_PATH];
	GetModuleFileNameW(
		reinterpret_cast<HINSTANCE>(&__ImageBase),
		fileName,
		MAX_PATH 
	);
	return QFileInfo(QString::fromWCharArray(fileName));
}
	
#endif


// constructor
TextureTsne::TextureTsne(
	bool verbose, 
	int iterations, 
	int num_target_dimensions,
	int perplexity,
	int exaggeration_iter,
	double theta
) : _verbose(verbose), _iterations(iterations), _num_target_dimensions(num_target_dimensions),
	_perplexity(perplexity), _exaggeration_iter(exaggeration_iter), _theta(theta)
{
}
	
// tSNE transform and return results
// Only accept c-type float (row-major, dense) and cast any non conforming args. 
// Return a numpy compatible array.
//py::array_t<float, py::array::c_style>
py::array_t<float, py::array::c_style> TextureTsne::fit_transform(
	py::array_t<float, py::array::c_style | py::array::forcecast> X) 
{
	QFileInfo libInfo = get_lib_info();
	QApplication::
	//std::cout << "set library path with " << libInfo.absolutePath().toStdString() << std::endl;
	//
	QApplication::addLibraryPath(libInfo.absolutePath());
	char *dllPath = const_cast<char *>(libInfo.absolutePath().toStdString().c_str());
	int argc = 1;
	QApplication _app(argc, static_cast<char **>(&dllPath));
	
	_app.setQuitOnLastWindowClosed(false);
	QApplication::setApplicationName("TextureTsne tSNE");
	QApplication::setApplicationVersion("0.0.1");

	auto X_loc = X;
	float similarities_comp_time = 0;
	float gradient_desc_comp_time = 0;
	typedef float scalar_type;
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
    hdi::dr::HDJointProbabilityGenerator<scalar_type>::sparse_scalar_matrix_type distributions;
    hdi::dr::HDJointProbabilityGenerator<scalar_type>::Parameters prob_gen_param;
	hdi::dr::GradientDescentTSNETexture tSNE;
	hdi::dr::TsneParameters tSNE_param;
    hdi::data::Embedding<scalar_type> embedding;
	std::cout << "knn starting" << "\n";
    {
		hdi::utils::ScopedTimer<float,hdi::utils::Seconds> timer(similarities_comp_time);
		prob_gen_param._perplexity = _perplexity;
		prob_gen.computeProbabilityDistributions(
			static_cast<float *>(X_info.ptr),
			_num_dimensions,
			_num_data_points,
			distributions,
			prob_gen_param);
    }

	std::cout << "knn complete" << "\n";
	OffscreenBuffer _offscreen;
	_offscreen.bindContext();
	std::cout << "grad descent tsne starting" << "\n";
    {
		hdi::utils::ScopedTimer<float,hdi::utils::Seconds> timer(gradient_desc_comp_time);
		tSNE_param._embedding_dimensionality = _num_target_dimensions;
		tSNE_param._mom_switching_iter = _exaggeration_iter;
		tSNE_param._remove_exaggeration_iter = _exaggeration_iter;
		tSNE.initialize(distributions,&embedding,tSNE_param);
		//tSNE.setTheta(_theta);
		
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
		std::cout << "Similarities computation (sec) " << similarities_comp_time << "\n";
		std::cout << "Gradient descent (sec) " << gradient_desc_comp_time << "\n";
	}
	QMetaObject::invokeMethod(&_app, "quit", Qt::QueuedConnection);
	_app.exec();
	return result;
}
