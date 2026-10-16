from __future__ import annotations

import pytest

from PIL import ImageTiles


def test_tile_count_exact_division() -> None:
    assert ImageTiles.tile_count((8, 6), (2, 2)) == (4, 3)


def test_tile_count_partial_edges() -> None:
    assert ImageTiles.tile_count((10, 10), (4, 4)) == (3, 3)


def test_tile_count_partial_one_axis() -> None:
    assert ImageTiles.tile_count((10, 8), (4, 4)) == (3, 2)


def test_tile_count_rectangular_tiles() -> None:
    assert ImageTiles.tile_count((10, 7), (3, 4)) == (4, 2)


def test_tile_count_tile_larger_than_image() -> None:
    assert ImageTiles.tile_count((5, 3), (8, 8)) == (1, 1)


def test_tile_count_tile_larger_on_one_axis() -> None:
    assert ImageTiles.tile_count((5, 8), (8, 3)) == (1, 3)
    assert ImageTiles.tile_count((9, 2), (4, 5)) == (3, 1)


@pytest.mark.parametrize(
    "image_size,tile_size",
    (
        ((0, 4), (2, 2)),
        ((-1, 4), (2, 2)),
        ((4, 0), (2, 2)),
        ((4, -1), (2, 2)),
        ((4, 4), (0, 2)),
        ((4, 4), (-2, 2)),
        ((4, 4), (2, 0)),
        ((4, 4), (2, -3)),
    ),
)
def test_tile_count_non_positive_dimensions(
    image_size: tuple[int, int], tile_size: tuple[int, int]
) -> None:
    with pytest.raises(
        ValueError, match="image and tile dimensions must be greater than 0"
    ):
        ImageTiles.tile_count(image_size, tile_size)
