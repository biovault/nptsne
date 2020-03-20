#include "SparseTsne.h"
#include <hdi/utils/log_helper_functions.h>

void SparseTsne::initialize(sparse_scalar_matrix_type& sparse_matrix, uint32_t analysis_id, hdi::dr::TsneParameters params)
{
    _tSNE.setLogger(_logger);
    
    // The sparse matrix should have at least 7 entries
    // TODO repair this correctly
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
    double theta = 0;
    if(sparse_matrix.size() < 1000){
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
    
    _tSNE.setTheta(theta);
    hdi::utils::secureLogValue(_logger,"theta",theta);
    hdi::utils::secureLogValue(_logger,"exg",params._exaggeration_factor);


    _tSNE.initialize(sparse_matrix,&_embedding,params);

    _analysis_id = analysis_id;
}

void SparseTsne::doAnIteration()
{
    _tSNE.doAnIteration();  
}

