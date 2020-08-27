# -*- coding: utf-8 -*-
"""The configuration definitions for the demo software.
    Defines a hierarchy of named tuples to save and
    access predefined configurations readably

    Classes:
        Hsne
        Embedding
        PlainData
        MetaData
        LabelledData
        LabelledImage
        PointMeta
        HyperspectralImage

"""
from typing import NamedTuple


class Hsne(NamedTuple):
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
    hsne: Hsne
    embedding: Embedding
    image: ImageInfo


class PointMeta(NamedTuple):
    """The demo is multi-dimensional point data
        with meta data classes and colors"""
    descriptor: str
    data: MetaData
    hsne: Hsne
    embedding: Embedding


class HyperspectralImage(NamedTuple):
    """The demo is a hyperspectral image"""
    descriptor: str
    data: PlainData
    hsne: Hsne
    embedding: Embedding
    image: ImageInfo
