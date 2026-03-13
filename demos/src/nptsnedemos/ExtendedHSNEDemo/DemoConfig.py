# -*- coding: utf-8 -*-
"""Configuration for the demo"""
from pathlib import Path
from ConfigClasses import (
    LabelledImage,
    PointMeta,
    HyperspectralImage,
    LabelledData,
    MetaData,
    PlainData,
    HsneConfig,
    Embedding,
    ImageInfo,
)

root = Path(__file__).resolve().parent.parent

LABELLED_EXAMPLE = LabelledImage(
    "MNIST 70000 digits",
    LabelledData(str(root / "data/MNIST_70000.npy"), str(root / "data/MNIST_70000_label.npy")),
    HsneConfig(str(root / "data/MNIST_70000.hsne"), 3),
    Embedding(500),
    ImageInfo(28, 28),
)

POINT_EXAMPLE = PointMeta(
    "MTG cell data",
    MetaData(str(root / "data/datamat_overview.npy"), str(root / "data/metadata.csv")),
    HsneConfig(str(root / "data/datamat_overview.hsne"), 3),
    Embedding(500),
)

HYPERSPECTRAL_EXAMPLE = HyperspectralImage(
    "Hyperspectral sun (512x512)",
    PlainData(str(root / "data/small_sun.npy")),
    HsneConfig(str(root / "data/small_sun.hsne"), 4),
    Embedding(500),
    ImageInfo(512, 512),
)

DCMALL_EXAMPLE = HyperspectralImage(
    "DC Mall hyperspectral (1280x307)",
    PlainData(str(root / "data/dc_us.npy")),
    HsneConfig(str(root / "data/dc_us.hsne"), 4),
    Embedding(500),
    ImageInfo(1280, 307),
)

CONFIGS = [LABELLED_EXAMPLE, POINT_EXAMPLE, HYPERSPECTRAL_EXAMPLE, DCMALL_EXAMPLE]
