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
    m.attr("__all__") = py::make_tuple("KnnAlgorithm", "TextureTsne", "TextureTsneExtended", "HSne", "HSneScale", "_hsne_analysis");
    m.doc() = R"pbdoc(
        A numpy compatible python extension for GPGPU linear complexity tSNE and hSNE
        -----------------------------------------------------------------------------
    )pbdoc";

    // ENUMS
    py::enum_<KnnAlgorithm>(m, "KnnAlgorithm", py::arithmetic(), R"pbdoc(
            Enumeration used to select the knn algorithm used. Three possibilities are
            supported:

            `KnnAlgorithm.Flann`: Knn using FLANN - Fast Library for Approximate Nearest Neighbors
            `KnnAlgorithm.HNSW`: Knn using Hnswlib - fast approximate nearest neighbor search
            `KnnAlgorithm.Annoy`: Knn using Annoy - Spotify Approximate Nearest Neighbors Oh Yeah
        )pbdoc")
        .value("Flann", KnnAlgorithm::Flann)
        .value("HNSW", KnnAlgorithm::HNSW)
        .value("Annoy", KnnAlgorithm::Annoy);

    // CLASSES
    // Basic interface for GPU Texture based tSNE
    py::class_<TextureTsne> textureTsne(m, "TextureTsne",
        R"pbdoc(
            Create a wrapper class for the linear tSNE implementation.

            Parameters
            ----------
            verbose : bool
                Enable verbose logging to standard output
            iterations : int
                The number of iterations to perform. This must be at least 1000.
            num_target_dimensions : int
                The number of dimensions for the output embedding. Default is 2.
            perplexity : int
                The tSNE parameter that defines the neighborhood size. Usually between 10 and 30. Default is 30.
            exaggeration_iter : int
                The iteration when force exaggeration starts to decay.
            knn_algorithm : :class:`KnnAlgorithm`
                The knn algorithm used for the nearest neighbor calculation.
                The default is `Flann` for less than 50 dimensions `HNSW` may be faster

            Notes
            -----
            TextureTsne is a GPU compute shader implementation of the gradient descent
            linear tSNE. It is described in [1]_.

            See Also
            --------
            TextureTsneExtended

            References
            ----------
            .. [1] `GPGPU Linear Complexity t-SNE Optimization <https://doi.org/10.1109/TVCG.2019.2934307>`_

        )pbdoc");

    textureTsne.def(py::init<bool, int, int, int, int, KnnAlgorithm>(),
        R"pbdoc(
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

            Parameters
            ----------
            X : :class:`ndarray`
                The input data with shape (num. data points, num. dimensions)

            Returns
            -------
            :class:`ndarray`
                A numpy array contain a flatten (1D) embedding
        )pbdoc",
        py::arg("X"));

    // Extended TextureTsne interface for advanced use of GPU texture tSNE
    py::class_<TextureTsneExtended> textureTsneExtended(m, "TextureTsneExtended",
        R"pbdoc(
            Create an extended functionality wrapper for the linear tSNE implementation.

            Parameters
            ----------
            verbose : bool
                Enable verbose logging to standard output, default is False
            num_target_dimensions : int
                The number of dimensions for the output embedding. Default is 2.
            perplexity : int
                The tSNE parameter that defines the neighborhood size. Usually between 10 and 30. Default is 30.
            knn_algorithm : :class:`KnnAlgorithm`
                The knn algorithm used for the nearest neighbor calculation. The default is 'Flann' for less than 50 dimensions 'HNSW' may be faster

            Attributes
            ----------
            decay_started_at
            iteration_count

            Notes
            -----
            `TextureTsneExtended` offers additional control over the exaggeration decay
            compares to `TextureTsne`. Additionally it supports inputting an initial embedding.
            Linear tSNE is described in [1]_.

            See Also
            --------
            TextureTsne

            References
            ----------
            .. [1] `GPGPU Linear Complexity t-SNE Optimization <https://doi.org/10.1109/TVCG.2019.2934307>`_

        )pbdoc");

    textureTsneExtended.def(py::init<bool, int, int, KnnAlgorithm>(),
        R"pbdoc(

        )pbdoc",
        py::arg("verbose") = false,
        py::arg("num_target_dimensions") = 2,
        py::arg("perplexity") = 30,
        py::arg("knn_algorithm") = KnnAlgorithm::Flann);

    textureTsneExtended.def("init_transform",
        &TextureTsneExtended::init_transform,
        R"pbdoc(
            Initialize the transform with given data and optional initial embedding.
            Fit X into an embedded space and return that transformed output.

            Parameters
            ----------
            X : :class:`ndarray`
                The input data with shape (num. data points, num. dimensions)
            initial_embedding : :class:`ndarray`
                An optional initial embedding. Shape should be (num data points, num output dimensions)
        )pbdoc",
        py::arg("X"),
        py::arg("initial_embedding") = py::array_t<nptsne::ScalarType>({}));

    textureTsneExtended.def("run_transform", &TextureTsneExtended::run_transform,
        R"pbdoc(
            Run the transform gradient descent for a number of iterations
            with the current settings for exaggeration.

            Parameters
            ----------
            verbose : bool
                Enable verbose logging to standard output.
            iterations : int
                The number of iterations to run.

            Returns
            -------
            :class:`ndarray`
                A numpy array contain a flatten (1D) embedding.
                Coordinates are arranged: x0, y0, x, y1, ...
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

            Parameters
            ----------
            initial_embedding : :class:`ndarray`
                An optional initial embedding. Shape should be (num data points, num output dimensions)
        )pbdoc",
        py::arg("initial_embedding") = py::array_t<nptsne::ScalarType>({}));

    textureTsneExtended.def("start_exaggeration_decay", &TextureTsneExtended::start_exaggeration_decay,
        R"pbdoc(
            Enable exaggeration decay. Effective on next call to run_transform.
            Exaggeration decay is fixed at 150 iterations. This call is ony effective once.

            Raises
            ------
            RuntimeError
                If the decay is already active. This can be ignored.
        )pbdoc");

    textureTsneExtended.def_property_readonly("decay_started_at", &TextureTsneExtended::get_decay_started_at,
        R"pbdoc(
            int: The iteration number when exaggeration decay started.
            Is -1 if decays has not started.
        )pbdoc");

    textureTsneExtended.def_property_readonly("iteration_count", &TextureTsneExtended::get_iteration_count,
        R"pbdoc(
            int: The number of completed iterations of tSNE gradient descent.
        )pbdoc");

    textureTsneExtended.def("close", &TextureTsneExtended::close,
        R"pbdoc(
            Release GPU resources for the transform
        )pbdoc");

    // ******************************************************************
    // Hierarchical SNE wrapper
    py::class_<HSne> hsne_class(m, "HSne");

    hsne_class.doc() = R"pbdoc(
        Initialize an HSne wrapper with logging state.

        Parameters
        ----------
        verbose : bool
            Enable verbose logging to standard output, default is False

        Examples
        --------
        Create an HSNE wrapper

        >>> import doctest
        >>> import nptsne
        >>> doctest.ELLIPSIS_MARKER = '----'
        >>> hsne = nptsne.HSne(True)
     
        Attributes
        ----------
        num_data_points
        num_dimensions
        num_scales

        Notes
        -----
        HSne is a simple wrapper API for the Hierarchical SNE implementation.

        Hierarchical SNE is  is a GPU compute shader implementation of Hierarchical
        Stochastic Neighborhood Embedding described in [1]_.

        The wrapper can be
        used to create a new or load an existing hSNE analysis. The hSNE
        analysis is then held in the HSne instance and can be accessed through the
        class api.

        References
        ----------
        .. [1] `Hierarchical Stochastic Neighbor Embedding <https://doi.org/10.1111/cgf.12878>`_

        )pbdoc";

    hsne_class.def(py::init<bool>(),
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
                Create the hSNE analysis data hierarchy with user assigned point ids from the input data with the number of scales required.

                Parameters
                ----------
                X : :class:`ndarray`
                    The data used to create the saved file. Shape is : (num. data points, num. dimensions)

                num_scales : int
                    How many scales to create in the hsne analysis

                point_ids : :class:`ndarray`, optional
                    Array of ids associated with the data points

                Examples
                --------
                >>> import nptsne
                >>> hsne = nptsne.HSne(True)
                >>> hsne.create_hsne(sample_data, 3)
                True
                >>> hsne.num_data_points
                10000
                >>> hsne.num_dimensions
                16
                >>> hsne.num_scales
                3
            
            )pbdoc",
            py::arg("X"),
            py::arg("num_scales"),
            py::arg("point_ids"))
        .def("load_hsne",
            &HSne::load_hsne,
            R"pbdoc(
                Load the hSNE analysis data hierarchy from a pre-existing hsne file.

                Parameters
                ----------
                X : :class:`ndarray`
                    The data used to create the saved file. Shape is : (num. data points, num. dimensions)
                file_path : str
                    Path to saved hSNE file

                Examples
                --------
                Load hsne from a file, and check that is contains the expected data

                >>> import nptsne
                >>> import doctest
                >>> loaded_hsne = nptsne.HSne(True)
                >>> loaded_hsne.load_hsne(sample_data, sample_hsne_file)  # doctest: +ELLIPSIS
                True
                >>> loaded_hsne.num_data_points
                10000
                >>> loaded_hsne.num_dimensions
                16
                >>> loaded_hsne.num_scales
                3

            )pbdoc",
            py::arg("X"),
            py::arg("file_path"));

    hsne_class.def_static("read_num_scales",
        static_cast<int (*)(const std::string&)>(&HSne::read_num_scales),
        R"pbdoc(
            Read the number of scales defined in stored hSNE data without fully loading the file.

            Parameters
            ----------
            filename : str
                The path to a saved hSNE

            Examples
            --------
            Read the number of scales from a saved file

            >>> import nptsne
            >>> nptsne.HSne.read_num_scales(sample_hsne_file)
            3

            Returns
            -------
            int
                The number of scales in the saved hierarchy

        )pbdoc",
        py::arg("file_path"));

    hsne_class.def("save", &HSne::save_to_file,
        R"pbdoc(
            Save the HSNE as a binary structure to a file

            Parameters
            ----------
            filename : str
                The file to save to. If it already exists it is overwritten.

            Examples
            --------
            Save the hsne to a file and check the number of scales was sved correctly.

            >>> import nptsne
            >>> sample_hsne.save("save_test.hsne")
            >>> nptsne.HSne.read_num_scales("save_test.hsne")
            3

        )pbdoc",
        py::arg("file_path"));

    hsne_class.def("get_scale", &HSne::get_scale,
        R"pbdoc(
            Get the scale information at the index. 0 is the HSNE data scale.

            Parameters
            ----------
            scale_index : int
                Index of the scale to retrieve

            Examples
            -------
            The number of landmarks in scale 0 is the number of data points.

            >>> scale = sample_hsne.get_scale(0)
            >>> scale.num_points
            10000

            Returns
            -------
            :class:`HSneScale`
                A numpy array contain a flatten (1D) embedding
        )pbdoc",
        py::arg("scale_number"));

    hsne_class.def_property_readonly("num_scales", &HSne::num_scales,
        R"pbdoc(
            int: The number of scales in the HSne.

            Examples
            -------

            >>> sample_hsne.num_scales
            3
        )pbdoc");
    hsne_class.def_property_readonly("num_data_points", &HSne::num_data_points,
        R"pbdoc(
            int: The number of data points in the HSne.

            Examples
            -------

            >>> sample_hsne.num_data_points
            10000
        )pbdoc");
    hsne_class.def_property_readonly("num_dimensions", &HSne::num_dimensions,
        R"pbdoc(
            int: The number of dimensions associated with the original data.

            Examples
            -------

            >>> sample_hsne.num_dimensions
            16
        )pbdoc");

    // ******************************************************************
    // Scale data for Hsne
    py::class_<HSneScale> hsne_scale_class(m, "HSneScale");

    hsne_scale_class.doc() = R"pbdoc(
        Wrap the HSNE data scale, returned from :func:`HSne.get_scale`.

        Attributes
        ----------
        num_points
        transition_matrix
        landmark_orig_indexes
        )pbdoc";

    hsne_scale_class.def_property_readonly("num_points", &HSneScale::num_points,
        R"pbdoc(
            int: The number of landmark points in this scale

            Examples
            -------

            >>> sample_scale0.num_points
            10000
        )pbdoc");

    hsne_scale_class
        .def("get_landmark_weight",
        [](HSneScale& self) {
            auto rows = self._scale._landmark_weight.size();
            return py::array_t<float>(
                { rows },
                { sizeof(float) },
                self._scale._landmark_weight.data(),
                py::cast(self));
        },
        R"pbdoc(
            The weights per landmark in the scale.

            Examples
            -------
            The size of landmark weights should match the number of points

            >>> num_points = sample_scale2.num_points
            >>> weights = sample_scale2.get_landmark_weight()
            >>> weights.shape[0] == num_points
            True

            All weights at scale 0 should be 1.0

            >>> weights = sample_scale0.get_landmark_weight()
            >>> test = weights[0] == 1.0
            >>> test.all()
            True

            Returns
            -------
            :class:`ndarray`
                Weights array in landmark index order

        )pbdoc");

    hsne_scale_class.def_property_readonly("transition_matrix",
        [](HSneScale& self) {
            nptsne::SparseScalarMatrixType& matrix = self.transition_matrix();
            std::vector<std::reference_wrapper<nptsne::MapStorageType >> sparse;
            for (uint32_t i = 0; i < matrix.size(); ++i) {
                sparse.push_back(matrix[i].memory());
            }
            return sparse;
        },
        R"pbdoc(
            The transition (probability) matrix in this scale.

            Examples
            -------
            The size of landmark weights should match the number of points

            >>> num_points = sample_scale2.num_points
            >>> matrix = sample_scale2.transition_matrix
            >>> len(matrix) == num_points
            True

            Notes
            -----
            The list returned has one entry for each landmark point, each entry is a list
            The inner list contains tuples where the first item
            is an integer landmark index in the scale and the second item
            is the transition matrix value for the two points.
            The resulting matrix is sparse

            Returns
            -------
            list(list(tuple)):
                The transition (probability) matrix in this scale

        )pbdoc");

    hsne_scale_class.def_property_readonly("landmark_orig_indexes",
        [](HSneScale& self) {
        auto rows = self._scale._landmark_to_original_data_idx.size();
        return py::array_t<unsigned int>(
            { rows },
            { sizeof(unsigned int) },
            self._scale._landmark_to_original_data_idx.data(),
            py::cast(self));
        }, ":class:`ndarray` : An ndarray of the original data indexes for each landmark in the scale");

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
        py::enum_<EmbedderType>(m_hsne, "EmbedderType", py::arithmetic(),
        R"pbdoc(
            Enumeration used to select the embedder used. Two possibilities are
            supported:

            `EmbedderType.CPU`: CPU tSNE
            `EmbedderType.CPU`: GPU tSNE

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
            Create a new analysis as a child of an (optional) parent analysis.          

            Parameters
            ----------
            hsne : :class:`HSne`
                The hierarchical SNE being explored
            embedder_type : :class:`EmbedderType`
                The tSNE to use CPU or GPU based
            parent : :class:`Analysis`, optional
                The parent Analysis (where the selection was performed) if any
            parent_selection : list, optional
                List of selection indexes in the parent analysis.

            Attributes
            ----------
            number_of_points
            parent_id
            transition_matrix
            landmark_weights
            landmark_indexes
            landmark_orig_indexes
            embedding

            Notes
            -----
            Together with `AnalysisModel` provides support for visual analytics of an hSNE.
            The Analysis class holds both the chosen landmarks at a particular
            scale but also permits referencing back to the original data.
            Additionally a t-SNE embedder is included (a choice is
            provided between GPU and CPU implementations) which can be used to create
            an embedding of the selected landmarks.

        )pbdoc");

        analysis_class.def(py::init([](
            HSne& hsne,
            EmbedderType embedder_type,
            Analysis* parent,
            std::vector<uint32_t> parent_selection) {
            return Analysis::make_analysis(hsne, embedder_type, parent, parent_selection);
        }),
            py::arg("hnse"),
            py::arg("embedder_type"),
            py::arg("parent")=nullptr,
            py::arg("parent_selection")=std::vector<uint32_t>());

        // The analysis properties
        analysis_class
            .def_readwrite("id", &Analysis::id)
            .def_readwrite("scale_id", &Analysis::scale_id);


        // Share the landmark weights without a copy
        analysis_class
            .def_property_readonly(
                "number_of_points",
                [](Analysis& self) {
                return self.landmark_indexes.size();
            }, "int : number of landmarks in this `Analysis`");

        analysis_class
            .def("__str__", &Analysis::toString);

        analysis_class
            .def("do_iteration", &Analysis::doAnIteration,
                "Perform one iteration of the chosen embedder");

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
            R"pbdoc(
                Get the area of influence of the selection in the original data.

                Parameters
                ----------
                select_list : list
                    A list of selection indexes for landmarks in this analysis

                Returns
                -------
                :class:`ndarray`
                    The indexes for the original points represented by the selected landmarks 
            )pbdoc",
            py::arg("select_list"));

        // id of the parent analysis (numeric_limits<uint32_t>::max if this is root)
        analysis_class.def_property_readonly(
            "parent_id",
            [](Analysis& self) {
            if (self.parent == nullptr) {
                return std::numeric_limits<uint32_t>::max();
            }
            return self.parent->id;
        }, "int : Unique id of the parent analysis");

        analysis_class.def_property_readonly("transition_matrix",
            [](Analysis& self) {
            nptsne::SparseScalarMatrixType& matrix = self.getTransitionMatrix();
            std::vector<std::reference_wrapper<nptsne::MapStorageType >> sparse;
            for (uint32_t i = 0; i < matrix.size(); ++i) {
                sparse.push_back(matrix[i].memory());
            }
            return sparse;
        }, "list(dict) : The transition (probability) matrix in this `Analysis`");

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
        }, ":class:`ndarray` : the weights for the landmarks in this `Analysis`");

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
        }, ":class:`ndarray` : the indexes for the landmarks in this `Analysis`");

        // Share the landmark original indexes without a copy
        // TODO change name to orig_index. Since this translates
        // selection indexes (not landmarks indexes) to original data
        // indexes
        analysis_class.def_property_readonly(
            "landmark_orig_indexes",
            [](Analysis& self) {
            auto rows = self.landmarks_orig_data.size();
            return py::array_t<unsigned int>(
                { rows },
                { sizeof(unsigned int) },
                self.landmarks_orig_data.data(),
                py::cast(self));
        }, ":class:`ndarray` : the original data indexes for the landmarks in this `Analysis`");

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
        }, ":class:`ndarray` : the tSNE embedding generated for this `Analysis`");

        // ******************************************************************
        // ***** CPU tSNE embedder mabe be used in hSNE analyses indtead of TextureTsne(Analysis class above) ******
        py::class_<SparseTsne> sparsetsne_class(m_hsne, "SparseTsne",
        R"pbdoc(
            SparseTsne a wrapper for an approximating tSNE CPU implementation.

            Forms an alternative to `TextureTsne` when GPU acceleration is not available

            Attributes
            ----------
            embedding : :class:`ndarray`
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
