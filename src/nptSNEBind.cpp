#include <pybind11/pybind11.h>
#include "TextureTsne.h"
#include "TextureTsneExtended.h"
#include <tuple>
namespace py = pybind11;

// Maintainer note - this uses Google style docstrings

PYBIND11_MODULE(nptsne, m) {
	
    m.doc() = R"doc(
        Nicola Pezzotti's texture tSNE via pybind11
        -------------------------------------------
		
		The package contains classes that wrap approximating tSNE
			and linear tSNE with APIs. The classes are:
			
			TextureTsne : linear tSNE simple API
			TextureTsneExtended : linear tSNE advanced API
			
		Reference: https://arxiv.org/abs/1805.10817

        .. currentmodule:: nptsne

        .. autosummary::
            :toctree: _generate
			
			TextureTsne
			TextureTsneExtended

    )doc";
	
	// ENUMS
	py::enum_<KnnAlgorithm>(m, "KnnAlgorithm", py::arithmetic())
		.value("Flann", KnnAlgorithm::Flann)
		.value("HNSW", KnnAlgorithm::HNSW);	
		
	// CLASSES
	py::class_<TextureTsne> textureTsne(m, "TextureTsne", R"doc(
	    TextureTsne: a simple wrapper API for the linear tSNE implementation.
		
		TextureTsne GPU compute shader implementation of the gradient descent
		linear tSNE described in doi://
		)doc");
		

	
	textureTsne.def(py::init<
			bool, int, int, int, int, KnnAlgorithm>(),
		R"doc(
		Args:
			verbose (bool): Enable verbose logging to std::out
			
			iterations (int): The number of iterations to perform. This must
				be at least 1000.
			
			num_target_dimensions (int): The number of dimensions for the output
				embedding. Default is 2.
			
			perplexity (int): The tSNE parameter that defines the neighborhood size.
				Usually between 10 and 30. Default is 30.
				
			exaggeration_iter (int): The iteration when force exaggeration starts 
				to decay.
			
			knn_algorithm (str): The knn algorithm used for the nearest neighbor
				calculation. The default is 'Flann' for less than 50 dimensions 
				'HNSW' may be faster 
		)doc",
		py::arg("verbose")=false, 
		py::arg("iterations")=1000,
		py::arg("num_target_dimensions")=2,
		py::arg("perplexity")=30,
		py::arg("exaggeration_iter")=250,
		py::arg("knn_algorithm")=KnnAlgorithm::Flann); 
		
	textureTsne.def("fit_transform", &TextureTsne::fit_transform, 
		R"doc(
		Fit X into an embedded space and return that transformed output.
		
		Args:
			X (ndarray) The iput data with shape (num. data points, num. dimensions)
		)doc",
		py::arg("X")

	);
	
	// Experimental extended TextureTsne 
	py::class_<TextureTsneExtended> textureTsneExtended(m, "TextureTsneExtended", R"doc(
	    TextureTsneExtended: an advanced wrapper API for the linear tSNE implementation.
		
		TextureTsneExtended offers additional control over the exaggeration decay
			along with the ability to input an initial embedding.
			Based on the linear tSNE algorithm described in doi://
		)doc");		
	
	textureTsneExtended.def(py::init<
			bool, int, int, KnnAlgorithm>(),
		R"doc(
		Args:
			verbose (bool): Enable verbose logging to std::out
			
			num_target_dimensions (int): The number of dimensions for the output
				embedding. Default is 2.
			
			perplexity (int): The tSNE parameter that defines the neighborhood size.
				Usually between 10 and 30. Default is 30.
			
			knn_algorithm (str): The knn algorithm used for the nearest neighbor
				calculation. The default is 'Flann' for less than 50 dimensions 
				'HNSW' may be faster 
		)doc", 
		py::arg("verbose")=false, 
		py::arg("num_target_dimensions")=2,
		py::arg("perplexity")=30,
		py::arg("knn_algorithm")=KnnAlgorithm::Flann);
		
	textureTsneExtended.def("init_transform", &TextureTsneExtended::init_transform, "Initialize the transform with given data and optional initial embedding",
		R"doc(
		Fit X into an embedded space and return that transformed output.
		Args:
			X (ndarray) The iput data with shape (num. data points, num. dimensions)
			
			initial_embedding(ndarray) An optional initial embedding. Shape should be 
				(num data points, num output dimensions)
		)doc",
		py::arg("X"),
		py::arg("initial_embedding")=py::array_t<TextureTsneExtended::scalar_type>({}));
	
	textureTsneExtended.def("run_transform", &TextureTsneExtended::run_transform, 
		R"doc(
		Run the transform gradient descent for a number of iterations 
		with the current settings for exaggeration.
		Args:
			verbose: Enable verbose logging to std:out
			
			iterations: the number of iterations to run 
		Returns:
			A numpy array contain a flatten (1D) embedding)doc",
		py::arg("verbose")=false, 
		py::arg("iterations")=1000);
		
	textureTsneExtended.def("start_exaggeration_decay", &TextureTsneExtended::start_exaggeration_decay, 
		R"doc(
		Enable exaggeration decay. Effective on next call to run_transform. 
		Exaggeration decay is fixed at 150 iterations. This call is ony effective once.
		Raises: RuntimeError if the decay is already active. This can be ignored.	
		)doc");

	textureTsneExtended.def_property_readonly("decay_started_at", &TextureTsneExtended::get_decay_started_at, 
		R"doc(The iteration number when exaggeration decay started. 
		Returns: 
			-1 if decays has not started.)doc");	
	
	textureTsneExtended.def_property_readonly("iteration_count", &TextureTsneExtended::get_iteration_count, 
		R"doc(The number of completed iterations of tSNE gradient descent.
		Returns:
			iteration_count)doc");	
	

	textureTsneExtended.def("close", &TextureTsneExtended::close, 
		R"doc(Release GPU resources for the transform)doc");

	
#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
