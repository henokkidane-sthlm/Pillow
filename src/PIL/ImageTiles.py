#
# The Python Imaging Library.
#
# Helpers for clamping crop boxes and splitting an image into tiles.
#
# Copyright (c) 2026 by Pillow contributors
#
# See the README file for information on usage and redistribution.
#
from __future__ import annotations


def clamp_box(
    box: tuple[int, int, int, int], size: tuple[int, int]
) -> tuple[int, int, int, int]:
    """
    Clamp a crop box so that it lies inside an image.

    Each edge is moved onto the nearest image boundary. ``right`` and
    ``lower`` are exclusive, matching :py:meth:`~PIL.Image.Image.crop`.

    :param box: The crop rectangle, as a (left, upper, right, lower)-tuple.
    :param size: The image size in pixels, given as a (width, height) tuple.
    :returns: The clamped (left, upper, right, lower) box.
    :raises ValueError: If ``size`` contains a negative dimension, or if the
        clamped box is inverted.
    """
    width, height = _image_size(size)
    left, upper, right, lower = box
    left = _clamp(left, width)
    upper = _clamp(upper, height)
    right = _clamp(right, width)
    lower = _clamp(lower, height)
    if right < left:
        msg = "Coordinate 'right' is less than 'left'"
        raise ValueError(msg)
    if lower < upper:
        msg = "Coordinate 'lower' is less than 'upper'"
        raise ValueError(msg)
    return left, upper, right, lower


def tile_boxes(size: tuple[int, int], tile: int) -> list[tuple[int, int, int, int]]:
    """
    Split an image into square tiles and return each tile's crop box.

    Tiles are ``tile`` pixels on each side and are ordered left to right,
    then top to bottom. A remainder along the right or bottom edge is kept
    as a smaller tile, clamped to the image, so the boxes cover every pixel
    exactly once. An image with a zero width or height has no tiles.

    :param size: The image size in pixels, given as a (width, height) tuple.
    :param tile: The square tile edge length, in pixels. Must be greater
        than 0.
    :returns: Clamped (left, upper, right, lower) boxes.
    :raises ValueError: If ``size`` contains a negative dimension, or if
        ``tile`` is not greater than 0.
    """
    if tile <= 0:
        msg = "tile size must be greater than 0"
        raise ValueError(msg)
    width, height = _image_size(size)
    if width == 0 or height == 0:
        return []

    return [
        clamp_box((left, upper, left + tile, upper + tile), (width, height))
        for upper in range(0, height, tile)
        for left in range(0, width, tile)
    ]


def tile_count(
    image_size: tuple[int, int], tile_size: tuple[int, int]
) -> tuple[int, int]:
    """
    Count how many tiles are needed to cover an image.

    ``columns`` is the number of tiles along the width and ``rows`` is the
    number along the height. A partial tile on the right or bottom edge
    counts as a tile. Tiles may be rectangular.

    :param image_size: The image size in pixels, given as a (width, height)
        tuple. Both dimensions must be greater than 0.
    :param tile_size: The tile size in pixels, given as a
        (tile_width, tile_height) tuple. Both dimensions must be greater
        than 0.
    :returns: ``(columns, rows)`` of tiles needed to cover the image.
    :raises ValueError: If any image or tile dimension is not greater than 0.
    """
    width, height = image_size
    tile_width, tile_height = tile_size
    if width <= 0 or height <= 0 or tile_width <= 0 or tile_height <= 0:
        msg = "image and tile dimensions must be greater than 0"
        raise ValueError(msg)
    return (
        _tile_count_axis(width, tile_width),
        _tile_count_axis(height, tile_height),
    )


def _clamp(value: int, limit: int) -> int:
    if value < 0:
        return 0
    if value > limit:
        return limit
    return value


def _image_size(size: tuple[int, int]) -> tuple[int, int]:
    width, height = size
    if width < 0 or height < 0:
        msg = "image size must be non-negative"
        raise ValueError(msg)
    return width, height


def _tile_count_axis(length: int, tile: int) -> int:
    return (length + tile - 1) // tile
