#include "SparseTsne.h"
#include <hdi/utils/log_helper_functions.h>
#include <iostream>

void SparseTsne::initialize(nptsne::sparse_scalar_matrix_type& sparse_matrix, uint32_t analysis_id, hdi::dr::TsneParameters params)
{
    _tSNE.setLogger(_logger);
    
    // The sparse matrix should have at least 7 entries
    // TODO repair this correctly
    std::cout << "Set the sparse matrix\n";
    for(int i = 0; i < sparse_matrix.size(); ++i){
        if(sparse_matrix[i].size() < 7){
            int to_add = 7 - sparse_matrix[i].size();
            for(int v = 0; v < to_add; ++v){
                int id = rand()%sparse_matrix.size();
                sparse_matrix[i][id] = 1./to_add;
            }

        }
    }

    // theta and the exaggeration factor are set based on the size of the data
    // Less than 1000 points: theta = 0 exaggeration = 1.5
    // 1000 to 15000 points:  theta scales up to 0.5 exaggeration scales up to 10
    // 15000 or more points: theta = 0.5 exaggeration = 10
    std::cout << "Determine the theta\n";
    double theta = 0;
    std::cout << "Sparse matrix size " << sparse_matrix.size() << std::endl;
    if(sparse_matrix.size() < 1000){
        std::cout << "Theta 0 exaggeration 1.5" << std::endl;
        theta = 0;
        params._exaggeration_factor = 1.5;
    }else if(sparse_matrix.size() < 15000){
        theta = (sparse_matrix.size()-1000.)/(15000.-1000.)*0.5;
        params._exaggeration_factor = 1.5+(sparse_matrix.size()-1000.)/(15000.-1000.)*8.5;
    }else{
        theta = 0.5;
        params._exaggeration_factor = 10;
    }
    params._remove_exaggeration_iter = 170;    
    
    std::cout << "Set tSNE theta" << std::endl;
    _tSNE.setTheta(theta);
    hdi::utils::secureLogValue(_logger,"theta",theta);
    hdi::utils::secureLogValue(_logger,"exg",params._exaggeration_factor);

    std::cout << "Initialize tSNE" << std::endl;
    _tSNE.initialize(sparse_matrix,&_embedding,params);
    std::cout << "Record the analysis id\n";
    _analysis_id = analysis_id;
}

void SparseTsne::doAnIteration()
{
    _tSNE.doAnIteration();  
}

