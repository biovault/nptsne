# -*- coding: utf-8 -*-
"""Configuration for the demo"""
from ConfigClasses import (LabelledImage, PointMeta, HyperspectralImage,
                           LabelledData, MetaData, PlainData,
                           Hsne, Embedding, ImageInfo)

LABELLED_EXAMPLE = LabelledImage(
    'MNIST 70000 digits',
    LabelledData('data/MNIST_70000.npy', 'data/MNIST_70000_label.npy'),
    Hsne('data/MNIST_70000.hsne', 3),
    Embedding(500),
    ImageInfo(28, 28)
)

POINT_EXAMPLE = PointMeta(
    'Motor cortex cell data',
    MetaData('data/datamat_overview.npy', 'data/metadata.csv'),
    Hsne('data/datamat_overview.hsne', 3),
    Embedding(500)
)

HYPERSPECTRAL_EXAMPLE = HyperspectralImage(
    'Hyperspectral sun (512x512)',
    PlainData('data/small_sun.npy'),
    Hsne('data/small_sun.hsne', 4),
    Embedding(500),
    ImageInfo(512, 512)
)

CONFIGS = [LABELLED_EXAMPLE,
           POINT_EXAMPLE,
           HYPERSPECTRAL_EXAMPLE]
