#include <pybind11/pybind11.h>
#include "TextureTsne.h"
#include "TextureTsneExtended.h"
#include <tuple>
namespace py = pybind11;

// Maintainer note - this uses Google style docstrings

PYBIND11_MODULE(_nptsne, m) {
    
    m.attr("__all__") = py::make_tuple("KnnAlgorithm", "TextureTsne", "TextureTsneExtended");    
    m.doc() = R"pbdoc(
        nptsne - A numpy compatible python extension for GPGPU linear complexity tSNE
        -----------------------------------------------------------------------------

        .. currentmodule:: nptsne

        .. autosummary::
             :toctree: _generate

             TextureTsne
             TextureTsneExtended


         The package contains classes that wrap linear complexity tSNE. 
         The classes are:
               
         TextureTsne : linear tSNE simple API
         TextureTsneExtended : linear tSNE advanced API
               
         Reference:  https://doi.org/10.1109/TVCG.2019.2934307 or (https://arxiv.org/abs/1805.10817v2)

    )pbdoc";
     
    // ENUMS
    py::enum_<KnnAlgorithm>(m, "KnnAlgorithm", py::arithmetic())
    .value("Flann", KnnAlgorithm::Flann)
    .value("HNSW", KnnAlgorithm::HNSW);

    // CLASSES
    py::class_<TextureTsne> textureTsne(m, "TextureTsne", R"pbdoc(
    TextureTsne: a simple wrapper API for the linear tSNE implementation.

        TextureTsne is a GPU compute shader implementation of the gradient descent
        linear tSNE described in https://doi.org/10.1109/TVCG.2019.2934307 or https://arxiv.org/abs/1805.10817v2

    )pbdoc");

    textureTsne.def(py::init<bool, int, int, int, int, KnnAlgorithm>(), 
    R"pbdoc(    
     :param verbose: Enable verbose logging to standard output
     :type verbose: bool

     :param iterations: The number of iterations to perform. This must be at least 1000.
     :type iterations: int

     :param num_target_dimensions: The number of dimensions for the output embedding. Default is 2.
     :type num_target_dimensions: int

     :param perplexity: The tSNE parameter that defines the neighborhood size. Usually between 10 and 30. Default is 30.
     :type perplexity: int

     :param exaggeration_iter: The iteration when force exaggeration starts to decay.
     :type exaggeration_iter: int

     :param knn_algorithm: The knn algorithm used for the nearest neighbor calculation. The default is 'Flann' for less than 50 dimensions 'HNSW' may be faster
     :type knn_algorithm: str

    )pbdoc",
    py::arg("verbose")=false,
    py::arg("iterations")=1000,
    py::arg("num_target_dimensions")=2,
    py::arg("perplexity")=30,
    py::arg("exaggeration_iter")=250,
    py::arg("knn_algorithm")=KnnAlgorithm::Flann);

    textureTsne.def("fit_transform", &TextureTsne::fit_transform, 
    R"pbdoc(
      Fit X into an embedded space and return that transformed output.

      :param X: The iput data with shape (num. data points, num. dimensions)
      :type X: ndarray
      
      :return: A numpy array contain a flatten (1D) embedding
      :rtype: ndarray

    )pbdoc",
    py::arg("X")
    );

    // Experimental extended TextureTsne
    py::class_<TextureTsneExtended> textureTsneExtended(m, "TextureTsneExtended", 
    R"pbdoc(
      TextureTsneExtended: an advanced wrapper API for the linear tSNE implementation.

      TextureTsneExtended offers additional control over the exaggeration decay
      along with the ability to input an initial embedding.
      Based on the linear tSNE algorithm described in https://arxiv.org/abs/1805.10817v2/

    )pbdoc");

    textureTsneExtended.def(py::init<bool, int, int, KnnAlgorithm>(), 
    R"pbdoc(
      :param verbose: Enable verbose logging to standard output
      :type verbose: bool

      :param num_target_dimensions: The number of dimensions for the output embedding. Default is 2.
      :type num_target_dimensions: int

      :param perplexity: The tSNE parameter that defines the neighborhood size. Usually between 10 and 30. Default is 30.
      :type perplexity: int

      :param knn_algorithm: The knn algorithm used for the nearest neighbor calculation. The default is 'Flann' for less than 50 dimensions 'HNSW' may be faster
      :type knn_algorithm: str

    )pbdoc",
    py::arg("verbose")=false,
    py::arg("num_target_dimensions")=2,
    py::arg("perplexity")=30,
    py::arg("knn_algorithm")=KnnAlgorithm::Flann);

    textureTsneExtended.def("init_transform", &TextureTsneExtended::init_transform, "Initialize the transform with given data and optional initial embedding", 
    R"pbdoc(
      Fit X into an embedded space and return that transformed output.
        
      :param X: The iput data with shape (num. data points, num. dimensions)
      :type X: ndarray

      :param initial_embedding: An optional initial embedding. Shape should be (num data points, num output dimensions)
      :type initial_embedding: ndarray

    )pbdoc",
    py::arg("X"),
    py::arg("initial_embedding")=py::array_t<TextureTsneExtended::scalar_type>({}));

    textureTsneExtended.def("run_transform", &TextureTsneExtended::run_transform, 
    R"pbdoc(
      Run the transform gradient descent for a number of iterations
      with the current settings for exaggeration.

      :param verbose: Enable verbose logging to standard output
      :type verbose: bool

      :param iterations: the number of iterations to run
      :type iterations: int
        
      :return: A numpy array contain a flatten (1D) embedding
      :rtype: ndarray

    )pbdoc",
    py::arg("verbose")=false,
    py::arg("iterations")=1000);
    
    textureTsneExtended.def("reinitialize_transform", &TextureTsneExtended::reinitialize_transform, "Reinitialize the transform with optional initial embedding", 
    R"pbdoc(
      Fit X into an embedded space and return that transformed output.
      Knn is not recomputed. If no initial_embedding is supplied the embedding
      is re-randomized.
        
      :param initial_embedding: An optional initial embedding. Shape should be (num data points, num output dimensions)
      :type initial_embedding: ndarray

    )pbdoc",
    py::arg("initial_embedding")=py::array_t<TextureTsneExtended::scalar_type>({}));    

    textureTsneExtended.def("start_exaggeration_decay", &TextureTsneExtended::start_exaggeration_decay, 
    R"pbdoc(
      Enable exaggeration decay. Effective on next call to run_transform.
      Exaggeration decay is fixed at 150 iterations. This call is ony effective once.
        
      Raises: RuntimeError if the decay is already active. This can be ignored.

    )pbdoc");

    textureTsneExtended.def_property_readonly("decay_started_at", &TextureTsneExtended::get_decay_started_at, 
    R"pbdoc(
      The iteration number when exaggeration decay started.
        
      :return: -1 if decays has not started.
      :rtype: int

    )pbdoc");

    textureTsneExtended.def_property_readonly("iteration_count", &TextureTsneExtended::get_iteration_count, 
    R"pbdoc(
      The number of completed iterations of tSNE gradient descent.
        
      :return: iteration_count
      :rtype: int
    )pbdoc");

    textureTsneExtended.def("close", &TextureTsneExtended::close, 
    R"pbdoc(
      Release GPU resources for the transform

    )pbdoc");

}
