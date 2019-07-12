#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
//#include "LibInfo.h"
#include <tuple>
//#include "OffscreenBuffer.h"
#include "KnnAlgorithm.h"
#include "hdi/data/embedding.h"
#include "hdi/dimensionality_reduction/hd_joint_probability_generator.h"
#include "hdi/dimensionality_reduction/gradient_descent_tsne_texture.h"
#include "glad/glad.h"
#include "GLFW/glfw3.h"

class TextureTsneExtended {
public:

	typedef float scalar_type;
	// constructor
	TextureTsneExtended(
		bool verbose=false,  
		int num_target_dimensions=2,
		int perplexity=30,
		KnnAlgorithm knn_algorithm=KnnAlgorithm::Flann
		);
	// Initialize the probabilities based on the data
	bool init_transform(
		py::array_t<float, py::array::c_style | py::array::forcecast> X,			
		py::array_t<float, py::array::c_style | py::array::forcecast> initial_embedding=py::array_t<scalar_type>({}));
		
	void start_exaggeration_decay();
	
	int get_decay_started_at();
	
	int get_iteration_count();	
	
	py::array_t<float, py::array::c_style> run_transform(
		bool verbose=false,  
		int iterations=1000);
		
	void close();
	
private:

	//OffscreenBuffer* _offscreen;
	hdi::dr::HDJointProbabilityGenerator<scalar_type>::sparse_scalar_matrix_type _distributions;
	hdi::data::Embedding<scalar_type> _embedding;
	hdi::dr::GradientDescentTSNETexture _tSNE;
	//std::unique_ptr<QApplication> _app;
	
	int _num_data_points;
    int _num_dimensions;
	int _iteration_count;
	bool _exaggeration_decay;
	int _decay_started_at;
    bool _verbose;
    int _iterations;
    int _perplexity;
	KnnAlgorithm _knn_algorithm;
    double _theta;
    int _num_target_dimensions;
	bool _have_preset_embedding;
    GLFWwindow* _offscreen_context;
};