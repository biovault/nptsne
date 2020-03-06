#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
#include "KnnAlgorithm.h"
//#include "OffscreenBuffer.h"
#include <hdi/dimensionality_reduction/hierarchical_sne.h>
#include <hdi/utils/cout_log.h>

class HSne {
public:

    typedef float scalar_type;
    typedef std::uint64_t DataPointID;
    typedef std::vector<hdi::data::MapMemEff<uint32_t, scalar_type> > probabilityMatrix_t;
    
    // The scale hierarchy data structures defined from the bottom up 
    // Data points...
    typedef std::vector<DataPointID> pointIdContainer_t;
    // ... are represented by landmarks ...
    typedef std::vector<pointIdContainer_t> landmarkContainer_t;
    // ... are contained at a different scales
    typedef std::vector<landmarkContainer_t> scalesContainer_t;
    
	// constructor
	HSne(
		bool verbose=false
	);
	
    // provided two overloaded init_hsne functions 
    // One without point ids (these default to 0 -> n-1)
    bool create_hsne(
        py::array_t<float, py::array::c_style | py::array::forcecast> X,
        int num_scales);
        
    bool create_hsne(
        py::array_t<float, py::array::c_style | py::array::forcecast> X,
        int num_scales,
        py::array_t<uint64_t, py::array::c_style | py::array::forcecast> point_ids);        
          
    //get_landmarks_at_scale(int scale_number);
    

    // save the raw hierarchy data to a file
    void save_to_file(const std::string &filePath);

	
private:
    int _num_scales;	
	int _num_data_points;
    int _num_dimensions;
    int _num_target_dimensions;    
    bool _verbose;
    int _seed;
    
    // The Hierarchical SNE algorithm
    hdi::dr::HierarchicalSNE<float, probabilityMatrix_t>* _hsne;
    
    // Hold the usersupplied or default point ids
    py::array_t<uint64_t, py::array::c_style | py::array::forcecast> *point_ids;
    
    hdi::dr::HierarchicalSNE<float, probabilityMatrix_t>::Parameters _hsneParams;
    
    std::vector< std::vector<float>* > _landmarkWeights;
    
    // This container holds the landmarks created by HSNE
    scalesContainer_t _derivedHierarchy;
    
    hdi::utils::CoutLog* _log;

  
    bool _init(
        py::array_t<float, py::array::c_style | py::array::forcecast> &X,
        uint64_t *point_ids,
        int num_point_ids);
    
    void set_default_hsne_params();
};

