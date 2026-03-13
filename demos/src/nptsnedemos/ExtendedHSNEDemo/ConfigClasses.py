# -*- coding: utf-8 -*-
"""The configuration definitions for the demo software.
    Defines a hierarchy of named tuples to save and
    access predefined configurations readably

    Classes:
        HsneConfig
        Embedding
        PlainData
        MetaData
        LabelledData
        LabelledImage
        PointMeta
        HyperspectralImage
        DemoType

"""
from typing import NamedTuple
from enum import Enum


class HsneConfig(NamedTuple):
    """Settings for the hsne"""

    hsne_file: str
    scales: int


class Embedding(NamedTuple):
    """Settings for the embedding"""

    iterations: int


class ImageInfo(NamedTuple):
    """Image dimension settings"""

    dim_x: int
    dim_y: int


class PlainData(NamedTuple):
    """Simply a data file"""

    data_file: str


class MetaData(NamedTuple):
    """Data and metadata files"""

    data_file: str
    meta_file: str


class LabelledData(NamedTuple):
    """Data and labelled files"""

    data_file: str
    label_file: str


class LabelledImage(NamedTuple):
    """The demo is a labelled image (MNIST style)"""

    descriptor: str
    data: LabelledData
    hsne: HsneConfig
    embedding: Embedding
    image: ImageInfo


class PointMeta(NamedTuple):
    """The demo is multi-dimensional point data
    with meta data classes and colors"""

    descriptor: str
    data: MetaData
    hsne: HsneConfig
    embedding: Embedding


class HyperspectralImage(NamedTuple):
    """The demo is a hyperspectral image"""

    descriptor: str
    data: PlainData
    hsne: HsneConfig
    embedding: Embedding
    image: ImageInfo


class DemoType(Enum):
    """The style of data being processed. Supported are
    Labelled: MNIST style data - with or without labels
    Point: e.g. cell and gene data wit meta data for labels/colors
    Hyperspectral images: Array of equally size images where each pixel has several
        dimensions (wavelengths)"""

    LABELLED_DEMO, POINT_DEMO, HYPERSPECTRAL_DEMO = range(3)
