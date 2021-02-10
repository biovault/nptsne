#include "KnnAlgorithm.h"
const std::string knn_library_to_string(hdi::dr::knn_library knn_algorithm) {
	switch(knn_algorithm) {
		case hdi::dr::knn_library::KNN_FLANN:
			return "flann";
		case hdi::dr::knn_library::KNN_HNSW:
			return "hnsw";
		case hdi::dr::knn_library::KNN_ANNOY:
			return "annoy";
		default:
            return "unknown KNN lib";
	}
}

const std::string knn_metric_to_string(hdi::dr::knn_distance_metric knn_algorithm) {
	switch(knn_algorithm) {
		case hdi::dr::knn_distance_metric::KNN_METRIC_EUCLIDEAN:
			return "euclidean";
		case hdi::dr::knn_distance_metric::KNN_METRIC_COSINE:
			return "cosine";
		case hdi::dr::knn_distance_metric::KNN_METRIC_INNER_PRODUCT:
			return "innerproduct";
		case hdi::dr::knn_distance_metric::KNN_METRIC_MANHATTAN:
			return "manhattan";
		case hdi::dr::knn_distance_metric::KNN_METRIC_HAMMING:
			return "hamming";
		case hdi::dr::knn_distance_metric::KNN_METRIC_DOT:
			return "dor";
		default:
            return "unknown KNN metric";
	}
}