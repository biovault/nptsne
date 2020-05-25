// Copyright 2020 LKEB at LUMC
// Author: B. van Lew
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  // automatic conversion of STL to list, set, tuple, dict
#include <pybind11/stl_bind.h>
#include "TextureTsne.h"
#include "TextureTsneExtended.h"
#include "HSne.h"
#include "Analysis.h"
#include "SparseTsne.h"
#include "Types.h"
#include <string>
#include <functional>
#include <tuple>
#include <limits>
namespace py = pybind11;

// Maintainer note - this uses Google style docstrings

PYBIND11_MODULE(_nptsne, m) {
    m.attr("__all__") = py::make_tuple("KnnAlgorithm", "TextureTsne", "TextureTsneExtended", "HSne", "_hsne_analysis");
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
        Enumeration used to select the knn algorithm used. Three possibilities are
        supported:

        :obj:`KnnAlgorithm.Flann`: Knn using FLANN - Fast Library for Approximate Nearest Neighbors

        :obj:`KnnAlgorithm.HNSW`: Knn using Hnswlib - fast approximate nearest neighbor search

        :obj:`KnnAlgorithm.Annoy`: Knn using Annoy - Spotify Approximate Nearest Neighbors Oh Yeah
    )pbdoc")
        .value("Flann", KnnAlgorithm::Flann)
        .value("HNSW", KnnAlgorithm::HNSW)
        .value("Annoy", KnnAlgorithm::Annoy);

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
        py::arg("verbose") = false,
        py::arg("iterations") = 1000,
        py::arg("num_target_dimensions") = 2,
        py::arg("perplexity") = 30,
        py::arg("exaggeration_iter") = 250,
        py::arg("knn_algorithm") = KnnAlgorithm::Flann);

    textureTsne.def("fit_transform", &TextureTsne::fit_transform,
        R"pbdoc(
      Fit X into an embedded space and return that transformed output.

      :param X: The iput data with shape (num. data points, num. dimensions)
      :type X: ndarray

      :return: A numpy array contain a flatten (1D) embedding
      :rtype: ndarray

    )pbdoc",
        py::arg("X"));

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
        py::arg("verbose") = false,
        py::arg("num_target_dimensions") = 2,
        py::arg("perplexity") = 30,
        py::arg("knn_algorithm") = KnnAlgorithm::Flann);

    textureTsneExtended.def("init_transform",
        &TextureTsneExtended::init_transform,
        "Initialize the transform with given data and optional initial embedding",
        R"pbdoc(
      Fit X into an embedded space and return that transformed output.

      :param X: The iput data with shape (num. data points, num. dimensions)
      :type X: ndarray

      :param initial_embedding: An optional initial embedding. Shape should be (num data points, num output dimensions)
      :type initial_embedding: ndarray

    )pbdoc",
        py::arg("X"),
        py::arg("initial_embedding") = py::array_t<nptsne::ScalarType>({}));

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
        py::arg("verbose") = false,
        py::arg("iterations") = 1000);

    textureTsneExtended.def("reinitialize_transform",
        &TextureTsneExtended::reinitialize_transform,
        "Reinitialize the transform with optional initial embedding",
        R"pbdoc(
          Fit X into an embedded space and return that transformed output.
          Knn is not recomputed. If no initial_embedding is supplied the embedding
          is re-randomized.

          :param initial_embedding: An optional initial embedding. Shape should be (num data points, num output dimensions)
          :type initial_embedding: ndarray

        )pbdoc",
        py::arg("initial_embedding") = py::array_t<nptsne::ScalarType>({}));

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

    // ******************************************************************
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
        py::arg("verbose") = false);

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
          Create the hSNE analysis data hierarchy with 0 -n-1 as point ids.

          :param X: The iput data with shape (num. data points, num. dimensions)
          :type X: ndarray

          :param num_scales: How many scales to create in the hsne analysis
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
          Create the hSNE analysis data hierarchy with user assigned point ids.

          :param X: The iput data with shape (num. data points, num. dimensions)
          :type X: ndarray

          :param num_scales: How many scales to create in the hsne analysis
          :type num_scales: int

          :param point_ids: The ids associated with the data points
          :type point_ids: ndarray

        )pbdoc",
            py::arg("X"),
            py::arg("num_scales"),
            py::arg("point_ids")
        )
        .def("create_hsne",
            py::overload_cast<
            py::array_t<float, py::array::c_style | py::array::forcecast>,
            const std::string&
            >(&HSne::create_hsne),
            R"pbdoc(
          Create the hSNE analysis data hierarchy with a pre-existing hsne file.

          :param X: The iput data with shape (num. data points, num. dimensions)
          :type X: ndarray

          :param file_path: Pre-calculates hsne file
          :type file_path: string
        )pbdoc",
            py::arg("X"),
            py::arg("file_path") );

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

    // ******************************************************************
    // Scale data for Hsne
    py::class_<HSneScale> hsne_scale_class(m, "HSneScale",
        R"pbdoc(
        HSneScale: a simple wrapper API for the HSNE data scale.

        )pbdoc");

    hsne_scale_class.def_property_readonly("num_points", &HSneScale::num_points, "The number of points in this scale");

    hsne_scale_class.def("get_landmark_weight", &HSneScale::getLandmarkWeight);

    hsne_scale_class.def_property_readonly("transition_matrix",
        [](HSneScale& self) {
        nptsne::SparseScalarMatrixType& matrix = self.transition_matrix();
        std::vector<std::reference_wrapper<nptsne::MapStorageType >> sparse;
        for (uint32_t i = 0; i < matrix.size(); ++i) {
            sparse.push_back(matrix[i].memory());
        }
        return sparse;
    });

    hsne_scale_class.def_property_readonly("landmark_orig_indexes",
        [](HSneScale& self) {
        auto rows = self._scale._landmark_to_original_data_idx.size();
        return py::array_t<unsigned int>(
            { rows },
            { sizeof(unsigned int) },
            self._scale._landmark_to_original_data_idx.data(),
            py::cast(self));
    });

    // ******************************************************************
    // pybind wrappers for hSNE analysis support submodule: hsne_analysis
    // The pybind submodule for the wrapped classes
    // has the _ prefix to mark it as private.
    // Wrapped classes are re-exported in the hsne_analysis/__init__.py
    // along with the pure python classes.
    py::module submod_hsne_analysis = m.def_submodule(
        "_hsne_analysis", "Extension functionality for navigating HSNE analysis");

    // TODO(B.van_Lew): Prototype shortcut: the hsne_analysis classes are defined here nested
    // Consider moving to a separate file.
    auto pybind_hsne_analysis = [](py::module &m_hsne) {
        // ENUMS
        py::enum_<EmbedderType>(m_hsne, "EmbedderType", py::arithmetic(), R"pbdoc(
            Enumeration used to select the embedder used. Two possibilities are
            supported:

            :obj:`EmbedderType.CPU`: CPU tSNE

            :obj:`EmbedderType.CPU`: GPU tSNE

        )pbdoc")
            .value("CPU", EmbedderType::CPU)
            .value("GPU", EmbedderType::GPU);

        // ***** A selection driven hSNE analysis ******
        // The classes are defined at the level of the submodule
        m_hsne.attr("__all__") = py::make_tuple("Analysis", "SparseTsne", "EmbedderType");

        // ******************************************************************
        // Note that parent None is allowed for creation of the top
        // level analysis.
        py::class_<Analysis> analysis_class(m_hsne, "Analysis",
            R"pbdoc(
            Analysis: a simple wrapper for a selection based hSNE analysis.

            )pbdoc");

        // Two possible init methods - one for a full analysis and one for the top level analysis (no parent)
        analysis_class.def(py::init([](
            HSne& hsne,
            EmbedderType embedder_type,
            Analysis* parent,
            std::vector<uint32_t> parent_selection) {
            return Analysis::make_analysis(hsne, embedder_type, parent, parent_selection);
        }),
            R"pbdoc(
         A new analysis as a child of a parent analysis. The parent selection
         are the landmark indexes in the parent analysis scale.

         :param hsne: The hierarchical SNE being explored
         :type hsne: HSne

         :param embedder_type: The tSNE to use CPU or GPU based
         :type embedder_type: EmbedderType

         :param parent: the parent Analysis (where the selection was performed) if any
         :type parent: Analysis

         :param parent_selection: List of parent selection indexes.
         :type parent_selection: list

        )pbdoc",
            py::arg("hnse"),
            py::arg("embedder_type"),
            py::arg("parent"),
            py::arg("parent_selection"))
            .def(py::init([](
                HSne& hsne,
                EmbedderType embedder_type) {
            return Analysis::make_analysis(hsne, embedder_type);
        }),
                R"pbdoc(
          A new top level analysis there is no parent analysis or parent selection.

         :param hsne: The hierarchical SNE being explored
         :type hsne: HSne

         :param embedder_type: The tSNE to use CPU or GPU based
         :type embedder_type: EmbedderType
        )pbdoc",
            py::arg("hnse"),
            py::arg("embedder_type"));

        // The analysis properties
        analysis_class
            .def_readwrite("id", &Analysis::id)
            .def_readwrite("scale_id", &Analysis::scale_id);


        // Share the landmark weights without a copy
        analysis_class.def_property_readonly(
            "number_of_points",
            [](Analysis& self) {
            return self.landmark_indexes.size();
        });

        analysis_class
            .def("__str__", &Analysis::toString);

        analysis_class
            .def("do_iteration", &Analysis::doAnIteration);

        analysis_class
            .def("get_area_of_influence",
                [](Analysis& self, std::vector<nptsne::UnsignedIntType> selection_list) {
                    std::vector<nptsne::ScalarType> aoi;
                    self.hsne->getAreaOfInfluenceTopDown(self.scale_id, selection_list, aoi);
                    py::array_t<nptsne::ScalarType> result = py::array_t<nptsne::ScalarType>(aoi.size());
                    auto result_info = result.request();
                    nptsne::ScalarType *output = static_cast<nptsne::ScalarType *>(result_info.ptr);
                    for (size_t i = 0; i < aoi.size(); ++i) {
                        output[i] = aoi[i];
                    }
                    return result;
            },
            py::arg("select_list"));

        // id of the parent analysis (numeric_limits<uint32_t>::max if this is root)
        analysis_class.def_property_readonly(
            "parent_id",
            [](Analysis& self) {
            if (self.parent == nullptr) {
                return std::numeric_limits<uint32_t>::max();
            }
            return self.parent->id;
        });

        analysis_class.def_property_readonly("transition_matrix",
            [](Analysis& self) {
            nptsne::SparseScalarMatrixType& matrix = self.getTransitionMatrix();
            std::vector<std::reference_wrapper<nptsne::MapStorageType >> sparse;
            for (uint32_t i = 0; i < matrix.size(); ++i) {
                sparse.push_back(matrix[i].memory());
            }
            return sparse;
        });

        // Share the landmark weights without a copy
        analysis_class.def_property_readonly(
            "landmark_weights",
            [](Analysis& self) {
            auto rows = self.landmark_weights.size();
            return py::array_t<float>(
                { rows },
                { sizeof(float) },
                self.landmark_weights.data(),
                py::cast(self));
        });

        // Share the landmark indexes without a copy
        analysis_class.def_property_readonly(
            "landmark_indexes",
            [](Analysis& self) {
            auto rows = self.landmark_indexes.size();
            return py::array_t<unsigned int>(
                { rows },
                { sizeof(unsigned int) },
                self.landmark_indexes.data(),
                py::cast(self));
        });

        // Share the landmark original indexes without a copy
        analysis_class.def_property_readonly(
            "landmark_orig_indexes",
            [](Analysis& self) {
            auto rows = self.landmarks_orig_data.size();
            return py::array_t<unsigned int>(
                { rows },
                { sizeof(unsigned int) },
                self.landmarks_orig_data.data(),
                py::cast(self));
        });

        // Share the embedding without a copy
        analysis_class.def_property_readonly(
            "embedding",
            [](Analysis& self) {
            auto cols = self.getEmbedding().numDimensions();
            auto rows = self.getEmbedding().numDataPoints();
            auto data_size = sizeof(float);
            // as a numpy array
            return py::array_t<float>(
                { rows, cols },
                { cols * data_size, data_size },
                self.getEmbedding().getContainer().data(),
                py::cast(self));
        });

        // ******************************************************************
        // ***** tSNE embedder used in hSNE analyses (Analysis class above) ******
        py::class_<SparseTsne> sparsetsne_class(m_hsne, "SparseTsne",
            R"pbdoc(
            Analysis: a simple wrapper for a selection based hSNE analysis.

            )pbdoc");

        sparsetsne_class.def("do_iteration", &SparseTsne::doAnIteration, "Perform a single tsne iteration",
            R"pbdoc(
          Perform a sinsle tSNE iteration on the sparse data.
          Once complete the embedding coordinates can be read via the embedding property
        )pbdoc");

        // Share the embedding without a copy
        sparsetsne_class.def_property_readonly(
            "embedding",
            [](SparseTsne& self) {
            auto cols = self.getEmbedding().numDimensions();
            auto rows = self.getEmbedding().numDataPoints();
            auto data_size = sizeof(float);
            // as a numpy array
            return py::array_t<float>(
                { rows, cols },
                { cols * data_size, data_size },
                self.getEmbedding().getContainer().data(),
                py::cast(self));
        },
            py::return_value_policy::reference_internal,
            "Embedding plot - shape embed dimensions x num points");
    };

    // bind the classes into the submodule
    pybind_hsne_analysis(submod_hsne_analysis);
}
