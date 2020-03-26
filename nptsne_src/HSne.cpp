#include "HSne.h"
#include <iostream>
#include <fstream>
#include <numeric>

HSne::HSne(
	bool verbose 
) : _num_scales(0), 
    _num_data_points(0),
    _num_dimensions(0),
    _num_target_dimensions(0),
    _verbose(verbose), 
    _seed(-1),
    _hsne(nullptr),
    point_ids(nullptr)
{
    set_default_hsne_params();
}


bool HSne::create_hsne(
    py::array_t<float, py::array::c_style | py::array::forcecast> X,
    int num_scales) 
{
    py::buffer_info X_info = X.request();
    _num_scales = num_scales;
    std::vector<uint64_t> point_ids(X_info.shape[0]);
    std::iota(point_ids.begin(), point_ids.end(), 0);
    return _init(X, point_ids.data(), X_info.shape[0]);
}

bool HSne::create_hsne(
    py::array_t<float, py::array::c_style | py::array::forcecast> X,
    int num_scales,
    py::array_t<uint64_t, py::array::c_style | py::array::forcecast> point_ids) 
{
    _num_scales = num_scales;
    py::buffer_info point_id_info = point_ids.request();
    int num_point_ids = point_id_info.shape[0];
    return _init(X, static_cast<uint64_t *>(point_id_info.ptr), num_point_ids);
}

void HSne::save_to_file(const std::string &filePath)
{
    if (_hsne == nullptr) {
        return;
    }
    std::ofstream out_stream(filePath, std::ios::binary);
    hdi::dr::IO::saveHSNE(*_hsne, out_stream, _log);
}

HSneScale HSne::get_scale(unsigned int scale_number)
{
    return HSneScale(_hsne->scale(scale_number));
}


bool HSne::_init(
    py::array_t<float, py::array::c_style | py::array::forcecast> &X,
    uint64_t *point_ids,
    int num_point_ids) 
{
    _log = new hdi::utils::CoutLog();
    if (nullptr == point_ids) {
        std::cout << "No point ids\n";
    }
    
    try {
        auto X_loc = X;
		py::buffer_info X_info = X_loc.request();
		if (X_info.ndim != 2) {
			throw std::runtime_error("Expecting input data to have two dimensions, data point and values");
		}
		_num_data_points = X_info.shape[0];
		_num_dimensions = X_info.shape[1];
        
        if (_hsne) { delete _hsne; _hsne = NULL; }

        _hsne = new hdi::dr::HierarchicalSNE<float, probabilityMatrix_t>();
        _hsne->setLogger(_log);
        _hsne->setDimensionality(_num_dimensions);

        _hsne->initialize(static_cast<float *>(X_info.ptr), _num_data_points, _hsneParams);
        _hsne->statistics().log(_log);

        _landmarkWeights.resize(_num_scales);

        for (int s = 0; s < _num_scales; ++s){
            _landmarkWeights[s] = NULL;
        }

        for (int s = 0; s < _num_scales-1; ++s){
            _hsne->addScale();
        }
	} 
	catch (const std::exception& e) {
		std::cout << "Fatal error: " << e.what() << std::endl;
		return false;
	}
	return true;        
}

void HSne::set_default_hsne_params()
{
    // TODO add interface for advanced user setting
    _hsneParams._seed = _seed;
	_hsneParams._num_walks_per_landmark = 100;
	_hsneParams._monte_carlo_sampling = true;
	_hsneParams._mcmcs_num_walks = 15;
	_hsneParams._mcmcs_landmark_thresh = 1.5;
	_hsneParams._mcmcs_walk_length = 15;
	_hsneParams._transition_matrix_prune_thresh = 0;
	_hsneParams._aknn_num_checks = 512;
	_hsneParams._out_of_core_computation = true; // to keep memory footprint small
	_hsneParams._aknn_algorithm = hdi::utils::knn_library::KNN_FLANN;
	_hsneParams._num_neighbors = 90;// TODO: set this value via interface or not at all
	_hsneParams._aknn_num_checks = 256;
	_hsneParams._aknn_num_trees = 3;
}