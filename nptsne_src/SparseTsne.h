// Class is a pared down version of N Pezzotti's MultiscaleEmbedderSingleView

#include <vector>
#include <hdi/dimensionality_reduction/sparse_tsne_user_def_probabilities.h>
#include <hdi/utils/cout_log.h>
#include <hdi/utils/abstract_log.h>
#include <hdi/data/map_mem_eff.h>

// Provides a wrapping for a sparse tSNE embedder
// The embedder can be initialized and per iteration the 
// intermediate embedding can be retrieved.
class SparseTsne final {
public:
    typedef float scalar_type;
    // a memory-efficient key => value map
    typedef hdi::data::MapMemEff<uint32_t,scalar_type> map_type;
    // use the memory-efficient map to hold sparse data 
    typedef std::vector<map_type> sparse_scalar_matrix_type;

    // a tSNE embedder that works with sparse data
    typedef hdi::dr::SparseTSNEUserDefProbabilities<scalar_type,sparse_scalar_matrix_type> tsne_type;
    
    typedef hdi::data::Embedding<scalar_type> embedding_type;
    
    SparseTsne() {};
    // No virtual destructor - we are final
    
    void initialize(sparse_scalar_matrix_type& sparse_matrix, uint32_t analysis_id, hdi::dr::TsneParameters params = hdi::dr::TsneParameters());
    
    void doAnIteration();
    
    embedding_type& getEmbedding() {return _embedding;}
    
    sparse_scalar_matrix_type& get_sparse_matrix() {return _sparse_matrix;}
    
    void setLogger(hdi::utils::AbstractLog* logger){
        _logger = logger; 
        _tSNE.setLogger(logger);
    }

private:
    tsne_type _tSNE;
    embedding_type _embedding;
    sparse_scalar_matrix_type _sparse_matrix;
    hdi::utils::AbstractLog* _logger;
    uint32_t _analysis_id;
};