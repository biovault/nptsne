#pragma once
#include "hdi/dimensionality_reduction/knn_utils.h"
#include "hdi/dimensionality_reduction/gradient_descent_tsne_texture.h"
#include <string>

const std::string knn_library_to_string(hdi::dr::knn_library knn_algorithm);

const std::string knn_metric_to_string(hdi::dr::knn_distance_metric knn_algorithm);

const std::string gpgpu_sne_type_to_string(hdi::dr::GradientDescentTSNETexture::GpgpuSneType gpgpu_sne_type);
