// Copyright 2020 LKEB at LUMC
// Author: B. van Lew
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // automatic conversion of STL to list, set, tuple, dict
#include <pybind11/stl_bind.h>
#include "TextureTsne.h"
#include "TextureTsneExtended.h"
#include "HSne.h"
#include "Analysis.h"
#include "SparseTsne.h"
#include "Types.h"
#include "hdi/dimensionality_reduction/knn_utils.h"
#include <string>
#include <algorithm>
#include <functional>
#include <tuple>
#include <limits>
namespace py = pybind11;

// Maintainer note - this uses Google style docstrings

PYBIND11_MODULE(_nptsne, m)
{
    // m.attr("__all__") = py::make_tuple("KnnAlgorithm", "KnnDistanceMetric", "TextureTsne", "TextureTsneExtended", "HSne", "HSneScale", "_hsne_analysis");
    m.doc() = R"pbdoc(
        A numpy compatible python extension for GPGPU linear complexity tSNE and HSNE
        -----------------------------------------------------------------------------
    )pbdoc";

    // ENUMS
    py::enum_<hdi::dr::knn_distance_metric> enumKDM(m, "KnnDistanceMetric", py::arithmetic(), R"pbdoc(
            Enumeration used to select the knn distance metric used. Five possibilities are
            supported:

            `KnnDistanceMetric.Euclidean`: Euclidean metric for all algorithms
            `KnnDistanceMetric.InnerProduct`: Inner Product metric for HNSW
            `KnnDistanceMetric.Cosine`: Cosine metric for Annoy
            `KnnDistanceMetric.Manhattan`: Manhattan metric for Annoy
            `KnnDistanceMetric.Hamming`: Hamming metric for Annoy, not supported
            `KnnDistanceMetric.Dot`: Dot metric for Annoy
        )pbdoc");

    enumKDM
        .value("Euclidean", hdi::dr::knn_distance_metric::KNN_METRIC_EUCLIDEAN)
        .value("Cosine", hdi::dr::knn_distance_metric::KNN_METRIC_COSINE)
        .value("InnerProduct", hdi::dr::knn_distance_metric::KNN_METRIC_INNER_PRODUCT)
        .value("Manhattan", hdi::dr::knn_distance_metric::KNN_METRIC_MANHATTAN)
        .value("Hamming", hdi::dr::knn_distance_metric::KNN_METRIC_HAMMING)
        .value("Dot", hdi::dr::knn_distance_metric::KNN_METRIC_DOT);

    py::enum_<hdi::dr::knn_library> enumKA(m, "KnnAlgorithm", py::arithmetic(), R"pbdoc(
            Enumeration used to select the knn algorithm used. Three possibilities are
            supported:

            `KnnAlgorithm.Flann`: Knn using FLANN - Fast Library for Approximate Nearest Neighbors
            `KnnAlgorithm.HNSW`: Knn using Hnswlib - fast approximate nearest neighbor search
            `KnnAlgorithm.Annoy`: Knn using Annoy - Spotify Approximate Nearest Neighbors Oh Yeah
        )pbdoc");

    enumKA
        .value("Flann", hdi::dr::knn_library::KNN_FLANN)
        .value("HNSW", hdi::dr::knn_library::KNN_HNSW)
        .value("Annoy", hdi::dr::knn_library::KNN_ANNOY)
        .def(
            "get_supported_metrics", [enumKDM](int knn_lib)
            {
                auto global = py::dict(py::module::import("__main__").attr("__dict__"));
                auto m = hdi::dr::supported_knn_library_distance_metrics(knn_lib);
                std::map<std::string, py::object> result;
                for (auto item : m)
                {
                    auto members = enumKDM.attr("__members__");
                    // The keys in the metrics map contain spaces e.g "Inner Product",
                    // the wrapped enum names don't because that
                    // does not work in python. Spaces are erased.
                    auto key = std::string(item.first);
                    key.erase(std::remove(key.begin(), key.end(), ' '), key.end());
                    auto enum_val = members[key.c_str()];
                    result[item.first] = enum_val;
                }
                return result;
            },
            R"pbdoc(
            Get a dict containing KnnDistanceMetric values supported by the KnnAlgorithm.

            Parameters
            ----------
            knn_lib : :class:`KnnAlgorithm`
                The algorithm being queried.

            Examples
            --------
            Each algorithm has different support. See the tests below.

            >>> import nptsne
            >>> support = nptsne.KnnAlgorithm.get_supported_metrics(nptsne.KnnAlgorithm.Flann)
            >>> for i in support.items():
            ...     print(i[0])
            Euclidean
            >>> support = nptsne.KnnAlgorithm.get_supported_metrics(nptsne.KnnAlgorithm.Annoy)
            >>> for i in support.items():
            ...     print(i[0])
            Cosine
            Dot
            Euclidean
            Manhattan
            >>> support = nptsne.KnnAlgorithm.get_supported_metrics(nptsne.KnnAlgorithm.HNSW)
            >>> for i in support.items():
            ...     print(i[0])
            Euclidean
            Inner Product
            >>> support["Euclidean"] is nptsne.KnnDistanceMetric.Euclidean
            True

            Returns
            -------
            :class:`ndarray`
                A numpy array contain a flatten (1D) embedding
        )pbdoc");

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
            knn_metric : :class:`KnnDistanceMetric`
                The knn distance metric used for the nearest neighbor calculation.
                The default is `KnnDistanceMetric.Euclidean` the only supported metric for `Flann`

            Examples
            --------
            Create an TextureTsne wrapper

            >>> import nptsne
            >>> tsne = nptsne.TextureTsne(verbose=True, knn_algorithm=nptsne.KnnAlgorithm.Annoy)
            >>> tsne.verbose
            True
            >>> tsne.iterations
            1000
            >>> tsne.num_target_dimensions
            2
            >>> tsne.perplexity
            30
            >>> tsne.exaggeration_iter
            250
            >>> tsne.knn_algorithm == nptsne.KnnAlgorithm.Annoy
            True

            Notes
            -----
            TextureTsne is a GPU compute shader implementation of the gradient descent
            linear tSNE. If the system does not support OpenGL 4.3 an abover the implementation
            falls back to the a Texture rendering approach as described in [1]_.

            See Also
            --------
            TextureTsneExtended

            References
            ----------
            .. [1] Pezzotti, N., Thijssen, J., Mordvintsev, A., Höllt, T., Van Lew, B., 
                Lelieveldt, B.P.F., Eisemann, E., Vilanova, A. 
                `GPGPU Linear Complexity t-SNE Optimization <https://doi.org/10.1109/TVCG.2019.2934307>`_
                IEEE Transactions on Visualization and Computer Graphics 26, 1172–1181

        )pbdoc");

    textureTsne.def(py::init<bool, int, int, int, int, hdi::dr::knn_library, hdi::dr::knn_distance_metric>(),
                    R"pbdoc(
        )pbdoc",
                    py::arg("verbose") = false,
                    py::arg("iterations") = 1000,
                    py::arg("num_target_dimensions") = 2,
                    py::arg("perplexity") = 30,
                    py::arg("exaggeration_iter") = 250,
                    py::arg("knn_algorithm") = hdi::dr::knn_library::KNN_FLANN,
                    py::arg("knn_metric") = hdi::dr::knn_distance_metric::KNN_METRIC_EUCLIDEAN);

    textureTsne.def("fit_transform", &TextureTsne::fit_transform,
                    R"pbdoc(
            Fit X into an embedded space and return that transformed output.

            Parameters
            ----------
            X : :class:`ndarray`
                The input data with shape (num. data points, num. dimensions)

            Examples
            --------
            An 2D embedding is returned in the form of a numpy array
            [x0, y0, x1, y1, ...].

            >>> import nptsne
            >>> tsne = nptsne.TextureTsne()
            >>> embedding = tsne.fit_transform(sample_tsne_data)  # doctest: +SKIP_IN_CI
            >>> embedding.shape  # doctest: +SKIP_IN_CI
            (4000,)
            >>> import numpy  # doctest: +SKIP_IN_CI
            >>> embedding.dtype == numpy.float32  # doctest: +SKIP_IN_CI
            True

            Returns
            -------
            :class:`ndarray`
                A numpy array contain a flatten (1D) embedding
        )pbdoc",
                    py::arg("X"));

    textureTsne.def_property_readonly("verbose", &TextureTsne::get_verbose,
                                      R"pbdoc(
            bool: True if verbose logging is enabled. Set at initialization.

            Examples
            --------

            >>> sample_texture_tsne.verbose
            False
        )pbdoc");

    textureTsne.def_property_readonly("num_target_dimensions", &TextureTsne::get_num_target_dimensions,
                                      R"pbdoc(
            int: The number of target dimensions, set at initialization.

            Examples
            --------

            >>> sample_texture_tsne.num_target_dimensions
            2
        )pbdoc");

    textureTsne.def_property_readonly("knn_algorithm", &TextureTsne::get_knn_algorithm,
                                      R"pbdoc(
            int: The KnnAlgorithm value, set at initialization.

            Examples
            --------

            >>> import nptsne
            >>> sample_texture_tsne.knn_algorithm == nptsne.KnnAlgorithm.Flann
            True
        )pbdoc");

    textureTsne.def_property_readonly("knn_distance_metric", &TextureTsne::get_knn_metric,
                                      R"pbdoc(
            int: KnnDistanceMetric value, set at initialization.

            Examples
            --------

            >>> import nptsne
            >>> sample_texture_tsne.knn_distance_metric == nptsne.KnnDistanceMetric.Euclidean
            True
        )pbdoc");

    textureTsne.def_property_readonly("iterations", &TextureTsne::get_iterations,
                                      R"pbdoc(
            int: The number of iterations, set at initialization.

            Examples
            --------

            >>> sample_texture_tsne.iterations
            1000
        )pbdoc");

    textureTsne.def_property_readonly("perplexity", &TextureTsne::get_perplexity,
                                      R"pbdoc(
            int: The tsne perplexity, set at initialization.

            Examples
            --------

            >>> sample_texture_tsne.perplexity
            30
        )pbdoc");

    textureTsne.def_property_readonly("exaggeration_iter", &TextureTsne::get_exaggeration_iter,
                                      R"pbdoc(
            int: The iteration where attractive force exaggeration starts to decay, set at initialization.

            Examples
            --------

            >>> sample_texture_tsne.exaggeration_iter
            250

            Notes
            -----
            The gradient of the cost function used to iteratively optimize the embedding points :math:`y_i`
            is a sum of an attractive and repulsive force :math:`\frac{\delta C} {\delta y_i} = 4(\phi * F_i ^{attr} - F_i ^{rep})`
            The iterations up to exaggeration_iter increase the :math:`F_i ^{attr}` term by the factor :math:`\phi`
            which then decays to 1.

        )pbdoc");

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
            knn_metric : :class:`KnnDistanceMetric`
                The knn distance metric used for the nearest neighbor calculation.
                The default is `KnnDistanceMetric.Euclidean` the only supported metric for `Flann`

            Attributes
            ----------
            decay_started_at
            iteration_count

            Examples
            --------
            Create an TextureTsneExtended wrapper

            >>> import nptsne
            >>> tsne = nptsne.TextureTsneExtended(verbose=True, num_target_dimensions=2, perplexity=35, knn_algorithm=nptsne.KnnAlgorithm.Annoy)
            >>> tsne.verbose
            True
            >>> tsne.num_target_dimensions
            2
            >>> tsne.perplexity
            35
            >>> tsne.knn_algorithm == nptsne.KnnAlgorithm.Annoy
            True

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
            .. [1] Pezzotti, N., Thijssen, J., Mordvintsev, A., Höllt, T., Van Lew, B., 
                Lelieveldt, B.P.F., Eisemann, E., Vilanova, A. 
                `GPGPU Linear Complexity t-SNE Optimization <https://doi.org/10.1109/TVCG.2019.2934307>`_
                IEEE Transactions on Visualization and Computer Graphics 26, 1172–1181

        )pbdoc");

    textureTsneExtended.def(py::init<bool, int, int, hdi::dr::knn_library, hdi::dr::knn_distance_metric>(),
                            R"pbdoc(

        )pbdoc",
                            py::arg("verbose") = false,
                            py::arg("num_target_dimensions") = 2,
                            py::arg("perplexity") = 30,
                            py::arg("knn_algorithm") = hdi::dr::knn_library::KNN_FLANN,
                            py::arg("knn_metric") = hdi::dr::knn_distance_metric::KNN_METRIC_EUCLIDEAN);

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

            Returns
            -------
            bool
                True if successful, False otherwise

            Examples
            --------
            Create an TextureTsneExtended wrapper and initialize the data. This step performs the knn.

            >>> import nptsne
            >>> tsne = nptsne.TextureTsneExtended()
            >>> tsne.init_transform(sample_tsne_data)
            True

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


            Examples
            --------
            Create an TextureTsneExtended wrapper and initialize the data and run for 250 iterations.

            >>> import nptsne
            >>> tsne = nptsne.TextureTsneExtended()
            >>> tsne.init_transform(sample_tsne_data)
            True
            >>> embedding = tsne.run_transform(iterations=250)    # doctest: +SKIP_IN_CI
            >>> embedding.shape    # doctest: +SKIP_IN_CI
            (4000,)
            >>> tsne.iteration_count    # doctest: +SKIP_IN_CI
            250

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

            Examples
            --------
            Create an TextureTsneExtended wrapper and initialize the data and run for 250 iterations.

            >>> import nptsne
            >>> tsne = nptsne.TextureTsneExtended()
            >>> tsne.init_transform(sample_tsne_data)
            True
            >>> embedding = tsne.run_transform(iterations=100)    # doctest: +SKIP_IN_CI
            >>> tsne.iteration_count    # doctest: +SKIP_IN_CI
            100
            >>> tsne.reinitialize_transform()    # doctest: +SKIP_IN_CI
            >>> tsne.iteration_count    # doctest: +SKIP_IN_CI
            0

        )pbdoc",
                            py::arg("initial_embedding") = py::array_t<nptsne::ScalarType>({}));

    textureTsneExtended.def("start_exaggeration_decay", &TextureTsneExtended::start_exaggeration_decay,
                            R"pbdoc(
            Enable exaggeration decay. Effective on next call to run_transform.
            From this point exaggeration decays over the following 150 iterations,
            the decay this is a fixed parameter.
            This call is ony effective once.

            Examples
            --------
            Starting decay exaggeration is recorded in the decay_started_at property.

            >>> import nptsne
            >>> tsne = nptsne.TextureTsneExtended()
            >>> tsne.init_transform(sample_tsne_data)
            True
            >>> tsne.decay_started_at
            -1
            >>> embedding = tsne.run_transform(iterations=100)    # doctest: +SKIP_IN_CI
            >>> tsne.start_exaggeration_decay()    # doctest: +SKIP_IN_CI
            >>> tsne.decay_started_at    # doctest: +SKIP_IN_CI
            100

            Raises
            ------
            RuntimeError
                If the decay is already active. This can be ignored.
        )pbdoc");

    textureTsneExtended.def_property_readonly("decay_started_at", &TextureTsneExtended::get_decay_started_at,
                                              R"pbdoc(
            int: The iteration number when exaggeration decay started.
            Is -1 if exaggeration decay has not started.

            Examples
            --------
            Starting decay exaggeration is recorded in the decay_started_at property.

            >>> sample_texture_tsne_extended.decay_started_at
            -1

        )pbdoc");

    textureTsneExtended.def_property_readonly("iteration_count", &TextureTsneExtended::get_iteration_count,
                                              R"pbdoc(
            int: The number of completed iterations of tSNE gradient descent.

            >>> sample_texture_tsne_extended.iteration_count
            0
        )pbdoc");

    textureTsneExtended.def("close", &TextureTsneExtended::close,
                            R"pbdoc(
            Release GPU resources for the transform
        )pbdoc");

    textureTsneExtended.def_property_readonly("verbose", &TextureTsneExtended::get_verbose,
                                              R"pbdoc(
            bool: True if verbose logging is enabled. Set at initialization.

            Examples
            --------

            >>> sample_texture_tsne_extended.verbose
            False
        )pbdoc");

    textureTsneExtended.def_property_readonly("num_target_dimensions", &TextureTsneExtended::get_num_target_dimensions,
                                              R"pbdoc(
            int: The number of target dimensions, set at initialization.

            Examples
            --------

            >>> sample_texture_tsne_extended.num_target_dimensions
            2
        )pbdoc");

    textureTsneExtended.def_property_readonly("knn_algorithm", &TextureTsneExtended::get_knn_algorithm,
                                              R"pbdoc(
            int: The KnnAlgorithm value, set at initialization.

            Examples
            --------

            >>> import nptsne
            >>> sample_texture_tsne_extended.knn_algorithm == nptsne.KnnAlgorithm.Flann
            True
        )pbdoc");

    textureTsneExtended.def_property_readonly("knn_distance_metric", &TextureTsneExtended::get_knn_metric,
                                              R"pbdoc(
            int: The KnnDistanceMetric value, set at initialization.

            Examples
            --------

            >>> import nptsne
            >>> sample_texture_tsne_extended.knn_distance_metric == nptsne.KnnDistanceMetric.Euclidean
            True
        )pbdoc");

    textureTsneExtended.def_property_readonly("perplexity", &TextureTsneExtended::get_perplexity,
                                              R"pbdoc(
            int: The tsne perplexity, set at initialization.

            Examples
            --------

            >>> sample_texture_tsne_extended.perplexity
            30
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

        >>> import nptsne
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
             (bool (HSne::*)(
                 py::array_t<float, py::array::c_style | py::array::forcecast>,
                 int)) &
                 HSne::create_hsne,
             py::arg("X"),
             py::arg("num_scales"))
        .def("create_hsne",
             (bool (HSne::*)(
                 py::array_t<float, py::array::c_style | py::array::forcecast>,
                 int,
                 py::array_t<uint64_t, py::array::c_style | py::array::forcecast>)) &
                 HSne::create_hsne,
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
                >>> hsne.create_hsne(sample_hsne_data, 3)
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
                Load the HSNE analysis data hierarchy from a pre-existing HSNE file.

                Parameters
                ----------
                X : :class:`ndarray`
                    The data used to create the saved file. Shape is : (num. data points, num. dimensions)
                file_path : str
                    Path to saved HSNE file

                Examples
                --------
                Load hsne from a file, and check that is contains the expected data

                >>> import nptsne
                >>> import doctest
                >>> loaded_hsne = nptsne.HSne(True)
                >>> loaded_hsne.load_hsne(sample_hsne_data, sample_hsne_file)  # doctest: +ELLIPSIS
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
                          static_cast<int (*)(const std::string &)>(&HSne::read_num_scales),
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
            Save the hsne to a file and check the number of scales was saved correctly.

            >>> import nptsne
            >>> from pathlib import Path
            >>> from tempfile import gettempdir
            >>> savepath = Path(gettempdir(), "save_test.hsne")
            >>> sample_hsne.save(str(savepath))
            >>> nptsne.HSne.read_num_scales(str(savepath))
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
            --------
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
            --------

            >>> sample_hsne.num_scales
            3
        )pbdoc");
    hsne_class.def_property_readonly("num_data_points", &HSne::num_data_points,
                                     R"pbdoc(
            int: The number of data points in the HSne.

            Examples
            --------

            >>> sample_hsne.num_data_points
            10000
        )pbdoc");
    hsne_class.def_property_readonly("num_dimensions", &HSne::num_dimensions,
                                     R"pbdoc(
            int: The number of dimensions associated with the original data.

            Examples
            --------

            >>> sample_hsne.num_dimensions
            16
        )pbdoc");

    // ******************************************************************
    // Scale data for Hsne
    py::class_<HSneScale> hsne_scale_class(m, "HSneScale");

    hsne_scale_class.doc() = R"pbdoc(
        Create a wrapper for the HSNE data scale. The function :func:`HSne.get_scale` works more directly than
        calling the constructor on this class.

        Parameters
        ----------
        hsne : :class:`HSne`
            The hierarchical SNE being explored
        scale_number : int
            The scale from the nsne to wrap

        Examples
        --------
        Using the initializer to create an HSneScale wrapper.
        Scale 0 contains the datapoints.  (Prefer the HSne.get_scale function)

        >>> import nptsne
        >>> scale = nptsne.HSneScale(sample_hsne, 0)
        >>> scale.num_points
        10000

        Attributes
        ----------
        num_points
        transition_matrix
        landmark_orig_indexes
        )pbdoc";

    hsne_scale_class.def(
        py::init([](
                     HSne &hsne,
                     int scale_number)
                 { return hsne.get_scale(scale_number); }),
        py::arg("hsne"),
        py::arg("scale_number"));

    hsne_scale_class.def_property_readonly("num_points", &HSneScale::num_points,
                                           R"pbdoc(
            int: The number of landmark points in this scale

            Examples
            --------

            >>> sample_scale0.num_points
            10000
        )pbdoc");

    hsne_scale_class
        .def(
            "get_landmark_weight",
            [](HSneScale &self)
            {
                auto rows = self._scale._landmark_weight.size();
                return py::array_t<float>(
                    {rows},
                    {sizeof(float)},
                    self._scale._landmark_weight.data(),
                    py::cast(self));
            },
            R"pbdoc(
            The weights per landmark in the scale.

            Examples
            --------
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

    hsne_scale_class.def_property_readonly(
        "transition_matrix",
        [](HSneScale &self)
        {
            nptsne::SparseScalarMatrixType &matrix = self.transition_matrix();
            std::vector<std::reference_wrapper<nptsne::MapStorageType>> sparse;
            for (uint32_t i = 0; i < matrix.size(); ++i)
            {
                sparse.push_back(matrix[i].memory());
            }
            return sparse;
        },
        R"pbdoc(
            The transition (probability) matrix in this scale.

            Examples
            --------
            The size of the transition matrix should match the number of points

            >>> sample_scale0.num_points == len(sample_scale0.transition_matrix)
            True
            >>> sample_scale1.num_points == len(sample_scale1.transition_matrix)
            True
            >>> sample_scale2.num_points == len(sample_scale2.transition_matrix)
            True

            Notes
            -----
            The list returned has one entry for each landmark point, each entry is a list
            The inner list contains tuples where the first item
            is an integer landmark index in the scale and the second item
            is the transition matrix value for the two points.

            The resulting matrix is sparse in list-of-lists (LIL) form, one list per row
            containing a list of (column number:value) tuples.

            Returns
            -------
            list(list(tuple)):
                The transition (probability) matrix in this scale in list-of-lists form

        )pbdoc");

    hsne_scale_class.def_property_readonly(
        "area_of_influence",
        [](HSneScale &self)
        {
            nptsne::SparseScalarMatrixType &matrix = self.area_of_influence();
            std::vector<std::reference_wrapper<nptsne::MapStorageType>> sparse;
            for (uint32_t i = 0; i < matrix.size(); ++i)
            {
                sparse.push_back(matrix[i].memory());
            }
            return sparse;
        },
        R"pbdoc(
            The area of influence matrix in this scale.

            Examples
            --------
            The size of landmark area of influence should match the number of points
            in the more detailed (s-1) scale.

            >>> len(sample_scale2.area_of_influence) == sample_scale1.num_points
            True

            Loop over all the landmarks, i, at scale 1.
            Sum the influences from each landmark j at scale 2 on 
            the individual landmarks i in scale 1.
            For each landmark i at scale 1 the total influence from the j
            landmarks should be approximately 1.0.
            In this random data test the difference is assumed 
            to be < :math:`1.5\mathrm{e}{-2}`.

            >>> aoi_2on1 = sample_scale2.area_of_influence
            >>> scale1_sum = {}
            >>> all_tots_are_1 = True
            >>> for i in aoi_2on1:
            ...     sum_inf = 0.0
            ...     for j_tup in i:
            ...         sum_inf += j_tup[1]
            ...     if abs(1 - sum_inf) > 0.015:
            ...         print(f"{1- sum_inf}")
            ...         all_tots_are_1 = False
            >>> all_tots_are_1 == True
            True

            Notes
            -----
            The return is in list-of-lists (LIL) format.
            The list returned has one entry for each landmark point i at scale s-1,
            :math: `\mathcal{L}_{i}^{s-1}`.
            Each entry is a list of tuples at where each tuple contains an index
            j for a landmark at scale s,   :math: `\mathcal{L}_{j}^{s}`
            and a value :math: `\mathit{I}^{S}(i,j)` representing the probability that the 
            landmark point i at scale s-1 is influenced by 
            landmark j at scale s.

            The resulting matrix is sparse.

            Returns
            -------
            list(list(tuple)):
                The area of influence matrix in this scale

        )pbdoc");

    hsne_scale_class.def_property_readonly(
        "landmark_orig_indexes",
        [](HSneScale &self)
        {
            auto rows = self._scale._landmark_to_original_data_idx.size();
            return py::array_t<unsigned int>(
                {rows},
                {sizeof(unsigned int)},
                self._scale._landmark_to_original_data_idx.data(),
                py::cast(self));
        },
        R"pbdoc(
            Original data indexes for each landmark in this scale.

            Examples
            --------
            At scale 0 the landmarks are all the data points.

            >>> sample_scale0.landmark_orig_indexes.shape
            (10000,)
            >>> sample_scale0.landmark_orig_indexes[0]
            0
            >>> sample_scale0.landmark_orig_indexes[9999]
            9999

            Returns
            -------
            :class:`ndarray`:
                An ndarray of the original data indexes.
        )pbdoc");

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
    auto pybind_hsne_analysis = [](py::module &m_hsne)
    {
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

            Examples
            --------
            The Analysis constructor is meant for use by the :class: `nptsne.hsne_analysis.AnalysisModel`.
            The example here illustrates how a top level analysis would be created from a sample hsne.

            >>> import nptsne
            >>> top_analysis = nptsne.hsne_analysis.Analysis(sample_hsne, nptsne.hsne_analysis.EmbedderType.CPU)
            >>> top_analysis.scale_id
            2
            >>> sample_hsne.get_scale(top_analysis.scale_id).num_points == top_analysis.number_of_points
            True

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
                                        HSne &hsne,
                                        EmbedderType embedder_type,
                                        Analysis *parent,
                                        std::vector<uint32_t> parent_selection)
                                    { return Analysis::make_analysis(hsne, embedder_type, parent, parent_selection); }),
                           py::arg("hnse"),
                           py::arg("embedder_type"),
                           py::arg("parent") = nullptr,
                           py::arg("parent_selection") = std::vector<uint32_t>());

        // The analysis properties
        analysis_class
            .def_readwrite("id", &Analysis::id,
                           R"pbdoc(
                int: Internally generated unique id for the analysis.

                Examples
                --------

                >>> sample_analysis.id
                0
            )pbdoc")
            .def_readwrite("scale_id", &Analysis::scale_id,
                           R"pbdoc(
                int: The number of this HSNE scale where this analysis is created.

                Examples
                --------
                >>> sample_analysis.scale_id
                2
            )pbdoc");

        // Share the landmark weights without a copy
        analysis_class
            .def_property_readonly(
                "number_of_points",
                [](Analysis &self)
                {
                    return self.landmark_indexes.size();
                },
                R"pbdoc(
                int : number of landmarks in this `Analysis`

                Examples
                --------
                The sample analysis is all the top scale points

                >>> sample_analysis.number_of_points == sample_scale2.num_points
                True
            )pbdoc");

        analysis_class
            .def("__str__", &Analysis::toString,
                 R"pbdoc(
                str: A string summary of the analysis.

                Examples
                --------
                >>> expected_str = 'Analysis[id={}, num points={}, scale={}]'.format(
                ... sample_analysis.id, 
                ... sample_analysis.number_of_points, 
                ... sample_analysis.scale_id)
                >>> str(sample_analysis) == expected_str
                True
            )pbdoc");

        analysis_class
            .def("do_iteration", &Analysis::doAnIteration,
                 "Perform one iteration of the chosen embedder");

        analysis_class
            .def(
                "get_area_of_influence",
                [](Analysis &self, std::vector<nptsne::UnsignedIntType> select_list,
                   double threshold = 0.3)
                {
                    std::vector<nptsne::ScalarType> aoi;
                    self.hsne->getAreaOfInfluenceTopDown(self.scale_id, select_list, aoi, threshold);
                    py::array_t<nptsne::ScalarType> result = py::array_t<nptsne::ScalarType>(aoi.size());
                    auto result_info = result.request();
                    nptsne::ScalarType *output = static_cast<nptsne::ScalarType *>(result_info.ptr);
                    for (size_t i = 0; i < aoi.size(); ++i)
                    {
                        output[i] = aoi[i];
                    }
                    return result;
                },
                R"pbdoc(
                Get the area of influence of the selection in the original data.
                For more information on the `threshold` refer to the HSNE paper
                section *4.2 Filtering and drilling down*.

                A fast but less accurate approach to obtaining area of influence 
                is `get_mapped_area_of_influence`.

                See Also
                --------
                get_mapped_area_of_influence

                Parameters
                ----------
                select_list : list
                    A list of selection indexes for landmarks in this analysis
                threshold: float, optional
                    The minimum value required for the underlying
                    datapoint to be considered in the landmark's region of influence.
                    Default is 0.3. The parameter must be in the range 0 to 1.0,
                    values outside the range it will be ignored.

                Returns
                -------
                :class:`ndarray`
                    The indexes for the original points represented by the selected landmarks
            )pbdoc",
                py::arg("select_list"),
                py::arg("threshold") = 0.3);

        analysis_class
            .def(
                "get_mapped_area_of_influence",
                [](Analysis &self, std::vector<nptsne::UnsignedIntType> select_list)
                {
                    std::vector<nptsne::UnsignedIntType> aoi;
                    self.hsne->getAreaOfInfluenceBottomUp(self.scale_id, select_list, aoi);
                    py::array_t<nptsne::UnsignedIntType> result = py::array_t<nptsne::UnsignedIntType>(aoi.size());
                    auto result_info = result.request();
                    nptsne::UnsignedIntType *output = static_cast<nptsne::UnsignedIntType *>(result_info.ptr);
                    for (size_t i = 0; i < aoi.size(); ++i)
                    {
                        output[i] = aoi[i];
                    }
                    return result;
                },
                R"pbdoc(
                Fast method to get the area of influence of the selection in the original data
                based on non overlapping :math:`{1}\rightarrow{n}` mapping of scale landmarks
                to original data points.

                This mapping is derived by working bottom up from the data points and finding 
                the landmarks at each scale with the maximum influence. The mapping is calculated
                once on the first call to this function so subsequent calls are fast.

                Due to thresholding it is possible that a datapoint may have no representative
                landmark at a specific scale.

                See Also
                --------
                get_area_of_influence

                Parameters
                ----------
                select_list : list
                    A list of selection indexes for landmarks in this analysis

                Examples
                --------

                Demonstrate the non-overlap of the area of influence for each landmark.

                >>> import math
                >>> import numpy as np
                >>> all_top_landmarks=list(range(0,sample_analysis.number_of_points))
                >>> all_influenced=sample_analysis.get_mapped_area_of_influence(all_top_landmarks)

                Assumes that at least 99% of the datapoints are in the AOI of the
                all toplevel landmarks.

                >>> all_influenced.shape[0] > math.floor(sample_scale0.num_points * 0.99)
                True

                Concatenating the individual landmark AOIs

                >>> infl_concat = np.empty((0,), dtype=np.uint32)
                >>> for i in all_top_landmarks:
                ...     influenced = sample_analysis.get_mapped_area_of_influence([i])
                ...     infl_concat = np.concatenate([infl_concat, influenced])

                Verify that all non-overlapping AOIs add to
                the same size as the total AOI

                >>> infl_concat.shape[0] == all_influenced.shape[0]
                True

                Concatenating the individual landmark AOIs gives the
                same list of datapoints as all the landmarks AOI.

                >>> all_influenced.sort()
                >>> infl_concat.sort()
                >>> (all_influenced == infl_concat).all()
                True

                Returns
                -------
                :class:`ndarray`
                    The indexes for the original points represented by the selected landmarks
            )pbdoc",
                py::arg("select_list"));

        // id of the parent analysis (numeric_limits<uint32_t>::max if this is root)
        analysis_class.def_property_readonly(
            "parent_id",
            [](Analysis &self)
            {
                if (self.parent == nullptr)
                {
                    return std::numeric_limits<uint32_t>::max();
                }
                return self.parent->id;
            },
            "int : Unique id of the parent analysis");

        analysis_class.def_property_readonly(
            "transition_matrix",
            [](Analysis &self)
            {
                nptsne::SparseScalarMatrixType &matrix = self.getTransitionMatrix();
                std::vector<std::reference_wrapper<nptsne::MapStorageType>> sparse;
                for (uint32_t i = 0; i < matrix.size(); ++i)
                {
                    sparse.push_back(matrix[i].memory());
                }
                return sparse;
            },
            "list(dict) : The transition (probability) matrix in this `Analysis`");

        // Share the landmark weights without a copy
        analysis_class.def_property_readonly(
            "landmark_weights",
            [](Analysis &self)
            {
                auto rows = self.landmark_weights.size();
                return py::array_t<float>(
                    {rows},
                    {sizeof(float)},
                    self.landmark_weights.data(),
                    py::cast(self));
            },
            R"pbdoc(
            :class:`ndarray` : the weights for the landmarks in this `Analysis`

            Examples
            --------
            There will be a weight for every point.

            >>> weights = sample_analysis.landmark_weights
            >>> weights.shape == (sample_analysis.number_of_points,)
            True
        )pbdoc");

        // Share the landmark indexes without a copy
        analysis_class.def_property_readonly(
            "landmark_indexes",
            [](Analysis &self)
            {
                auto rows = self.landmark_indexes.size();
                return py::array_t<unsigned int>(
                    {rows},
                    {sizeof(unsigned int)},
                    self.landmark_indexes.data(),
                    py::cast(self));
            },
            R"pbdoc(
            :class:`ndarray` : the indexes for the landmarks in this `Analysis`

            Examples
            --------
            In a complete top level analysis all points are present
            in this case all the points at scale2.

            >>> import numpy as np
            >>> np.array_equal(
            ... np.arange(sample_scale2.num_points, dtype=np.uint32), 
            ... sample_analysis.landmark_indexes)
            True
        )pbdoc");

        // Share the landmark original indexes without a copy
        // TODO change name to orig_index. Since this translates
        // selection indexes (not landmarks indexes) to original data
        // indexes
        analysis_class.def_property_readonly(
            "landmark_orig_indexes",
            [](Analysis &self)
            {
                auto rows = self.landmarks_orig_data.size();
                return py::array_t<unsigned int>(
                    {rows},
                    {sizeof(unsigned int)},
                    self.landmarks_orig_data.data(),
                    py::cast(self));
            },
            R"pbdoc(
            :class:`ndarray` : the original data indexes for the landmarks in this `Analysis`

            Examples
            --------
            The indexes are in the range of the original point indexes.

            >>> import numpy as np
            >>> np.logical_and(
            ... sample_analysis.landmark_orig_indexes >= 0,
            ... sample_analysis.landmark_orig_indexes < 10000).any()
            True
        )pbdoc");

        // Share the embedding without a copy
        analysis_class.def_property_readonly(
            "embedding",
            [](Analysis &self)
            {
                auto cols = self.getEmbedding().numDimensions();
                auto rows = self.getEmbedding().numDataPoints();
                auto data_size = sizeof(float);
                // as a numpy array
                return py::array_t<float>(
                    {rows, cols},
                    {cols * data_size, data_size},
                    self.getEmbedding().getContainer().data(),
                    py::cast(self));
            },
            R"pbdoc(
            :class:`ndarray` : the tSNE embedding generated for this `Analysis`

            Examples
            --------
            An embedding is a 2d float array. One entry per point.

            >>> import numpy as np
            >>> sample_analysis.embedding.shape == (sample_analysis.number_of_points, 2)
            True
            >>> sample_analysis.embedding.dtype == np.float32
            True
        )pbdoc");

        // ******************************************************************
        // ***** CPU tSNE embedder maybe be used in hSNE analyses indtead of TextureTsne(Analysis class above) ******
        py::class_<SparseTsne> sparsetsne_class(m_hsne, "SparseTsne",
                                                R"pbdoc(
            SparseTsne a wrapper for an approximating tSNE CPU implementation as described in [1]_.

            Forms an alternative to `TextureTsne` when GPU acceleration for creation of the embedding
            is not available for internal use in the `Analysis` class

            Attributes
            ----------
            embedding : :class:`ndarray`

            See Also
            --------
            Analysis
            EmbedderType

            References
            ----------
            .. [1] Pezzotti, N., Lelieveldt, B.P.F., Maaten, L. van der, Höllt, T., Eisemann, E., Vilanova, A., 2017.
                `Approximated and User Steerable tSNE for Progressive Visual Analytics. <https://doi.org/10.1109/TVCG.2016.2570755>`_
                IEEE Transactions on Visualization and Computer Graphics 23, 1739–1752.
        )pbdoc");

        sparsetsne_class.def("do_iteration", &SparseTsne::doAnIteration, "Perform a single tsne iteration",
                             R"pbdoc(
            Perform a sinsle tSNE iteration on the sparse data.
            Once complete the embedding coordinates can be read via the embedding property
        )pbdoc");

        // Share the embedding without a copy
        sparsetsne_class.def_property_readonly(
            "embedding",
            [](SparseTsne &self)
            {
                auto cols = self.getEmbedding().numDimensions();
                auto rows = self.getEmbedding().numDataPoints();
                auto data_size = sizeof(float);
                // as a numpy array
                return py::array_t<float>(
                    {rows, cols},
                    {cols * data_size, data_size},
                    self.getEmbedding().getContainer().data(),
                    py::cast(self));
            },
            py::return_value_policy::reference_internal,
            "Embedding plot - shape embed dimensions x num points");
    };

    // bind the classes into the submodule
    pybind_hsne_analysis(submod_hsne_analysis);
}
