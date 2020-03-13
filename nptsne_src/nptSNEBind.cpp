#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include "TextureTsne.h"
#include "TextureTsneExtended.h"
#include "HSne.h"
#include <tuple>
namespace py = pybind11;

// Maintainer note - this uses Google style docstrings

PYBIND11_MODULE(_nptsne, m) {
    
    m.attr("__all__") = py::make_tuple("KnnAlgorithm", "TextureTsne", "TextureTsneExtended", "HSne");    
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
    py::enum_<KnnAlgorithm>(m, "KnnAlgorithm", py::arithmetic(), R"pbdoc(
        Enumeration used to select the knn algorithm used. Two possibilities are
        supported:
        
        :obj:`KnnAlgorithm.Flann`: Knn using FLANN - Fast Library for Approximate Nearest Neighbors
        
        :obj:`KnnAlgorithm.HNSW`: Knn using Hnswlib - fast approximate nearest neighbor search
    )pbdoc")
    .value("Flann", KnnAlgorithm::Flann)
    .value("HNSW", KnnAlgorithm::HNSW);

    // CLASSES
    // Basic interface for GPU Texture based tSNE
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

    // Extended TextureTsne interface for advanced use of GPU texture tSNE
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
    
    // Hierarchical SNE wrapper
    py::class_<HSne> hsne_class(m, "HSne", 
        R"pbdoc(
        HSne: a simple wrapper API for the Hierarchical SNE implementation.

            Hierarchical SNE is  is a GPU compute shader implementation of Hierarchical
            Stochastic Neighborhood Embedding described in https://doi.org/10.1111/cgf.12878 

        )pbdoc");

    hsne_class.def(py::init<bool>(), 
        R"pbdoc(    
         :param verbose: Enable verbose logging to standard output
         :type verbose: bool
        )pbdoc",
        py::arg("verbose")=false);
  
    // create_hsne is overloaded - 
    // one overload uses default pointer
    // identifiers 0 -> num points - 1
    //
    hsne_class
    .def("create_hsne", 
        py::overload_cast<
            py::array_t<float, py::array::c_style | py::array::forcecast>,
            int
        >(&HSne::create_hsne), 
        R"pbdoc(
          Create the data hierarchy using hierarchical SNE.

          :param X: The iput data with shape (num. data points, num. dimensions)
          :type X: ndarray

          :param num_scales: The iput data with shape (num. data points, num. dimensions)
          :type num_scales: int
        )pbdoc",
        py::arg("X"),
        py::arg("num_scales")
    )
    .def("create_hsne", 
        py::overload_cast<
            py::array_t<float, py::array::c_style | py::array::forcecast>,
            int,
            py::array_t<uint64_t, py::array::c_style | py::array::forcecast>
        >(&HSne::create_hsne), 
        R"pbdoc(
          Create the data hierarchy using hierarchical SNE.

          :param X: The iput data with shape (num. data points, num. dimensions)
          :type X: ndarray

          :param num_scales: The iput data with shape (num. data points, num. dimensions)
          :type num_scales: int
          
          :param point_ids: The iput data with shape (num. data points, num. dimensions)
          :type point_ids: ndarray          

        )pbdoc",
        py::arg("X"),
        py::arg("num_scales"),
        py::arg("point_ids"));
        
    hsne_class.def("save", &HSne::save_to_file, "Save the HSNE hierarchy to a file", 
        R"pbdoc(
          Save the HSNE as a binary structure to a file
            
          :param filename: The iput data with shape (num. data points, num. dimensions)
          :type filename: string

        )pbdoc",
        py::arg("file_path"));
        
    hsne_class.def("get_scale", &HSne::get_scale, "Get the scale information at the index. 0 is the data scale",
        R"pbdoc(
          Get the scale at index
          
          :param scale_number
          :type scale_number unsigned int
            
          :return: A numpy array contain a flatten (1D) embedding
          :rtype: HSneScale

        )pbdoc",
        py::arg("scale_number"));  

    hsne_class.def_property_readonly("num_scales", &HSne::num_scales);
    hsne_class.def_property_readonly("num_data_points", &HSne::num_data_points);
    hsne_class.def_property_readonly("num_dimensions", &HSne::num_dimensions);
    
    // Scale data for Hsne
    py::class_<HSneScale> hsne_scale_class(m, "HSneScale", 
        R"pbdoc(
        HSneScale: a simple wrapper API for the HSNE data scale.

        )pbdoc");
    
    hsne_scale_class.def_property_readonly("num_points", &HSneScale::num_points, "The number of points in this scale");
    
    hsne_scale_class.def("get_landmark_weight", &HSneScale::getLandmarkWeight);
    
    // TODO scale navigation functions
    /*hsne_scale_class.def("get_selected_landmarks", &HSne::get_selected_landmarks, "Get the scale information at the index. 0 is the data scale",
        R"pbdoc(
          Get the scale at indes
          
          :param selection
          :type selection: ndarray
            
          :return: A numpy array contain a flatten (1D) embedding
          :rtype: HSneScale

        )pbdoc",
        py::arg("scale_number")); */   
}
