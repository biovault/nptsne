#include <pybind11/pybind11.h>
#include "TextureTsne.h"
#include "TextureTsneExtended.h"
#include <tuple>
namespace py = pybind11;

// Testing multiple return
/*
std::tuple<py::array_t<float>, py::array_t<float>> get_arrays(int size) {
	return std::make_tuple(
		py::array_t<float>(size),
		py::array_t<float>(size * 2)
	);
}
*/

PYBIND11_MODULE(nptsne, m) {
	// FUNCTIONS
	// Testing multiple returns
	// m.def("get_arrays", &get_arrays, "A function which get two empty numpy arrays", py::arg("size") = 1000);
	
	// CLASSES
	py::class_<TextureTsne> textureTsne(m, "TextureTsne");
	
	textureTsne.def(py::init<
			bool, int, int, int, int, int>(), 
		py::arg("verbose")=false, 
		py::arg("iterations")=1000,
		py::arg("num_target_dimensions")=2,
		py::arg("perplexity")=30,
		py::arg("exaggeration_iter")=250,
		py::arg("knn_algorithm")=-1); // -1 = flann, other value = hnswlib
		
	textureTsne.def("fit_transform", &TextureTsne::fit_transform, "Fit X into an embedded space and return that transformed output."

	);
	
	// Experimental extended TextureTsne 
	py::class_<TextureTsneExtended> textureTsneExtended(m, "TextureTsneExtended");
	
	textureTsneExtended.def(py::init<
			bool, int, int, int>(), 
		py::arg("verbose")=false, 
		py::arg("num_target_dimensions")=2,
		py::arg("perplexity")=30,
		py::arg("knn_algorithm")=-1);
		
	textureTsneExtended.def("init_transform", &TextureTsneExtended::init_transform, "Initialize the transform with given parameters.");
	
	textureTsneExtended.def("continue_transform", &TextureTsneExtended::run_transform, "Run the transform with the changeable params including optional embedding",
		py::arg("verbose")=false, 
		py::arg("iterations")=1000,
		py::arg("exaggeration_iter")=250,
		py::arg("embedding")=py::array_t<TextureTsneExtended::scalar_type>({}));
	
		
    m.doc() = R"pbdoc(
        Nicola Pezzotti's texture tSNE via pybind11
        -------------------------------------------

        .. currentmodule:: nptsne

        .. autosummary::
            :toctree: _generate

			__init__
            fit_transform
    )pbdoc";
	
#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}