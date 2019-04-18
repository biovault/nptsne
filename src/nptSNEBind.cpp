#include <pybind11/pybind11.h>
#include "TextureTsne.h"
namespace py = pybind11;

PYBIND11_MODULE(nptsne, m) {
	py::class_<TextureTsne> textureTsne(m, "TextureTsne");
	textureTsne.def(py::init<
			bool, int, int, int, int, double>(), 
		py::arg("verbose")=false, 
		py::arg("iterations")=1000,
		py::arg("num_target_dimensions")=2,
		py::arg("perplexity")=30,
		py::arg("exaggeration_iter")=250,
		py::arg("theta") = 0.5);
	textureTsne.def("fit_transform", &TextureTsne::fit_transform, "Fit X into an embedded space and return that transformed output.");
		
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