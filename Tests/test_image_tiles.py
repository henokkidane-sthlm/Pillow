from __future__ import annotations

import pytest

from PIL import Image, ImageTiles


def test_clamp_box_inside() -> None:
    assert ImageTiles.clamp_box((2, 3, 6, 7), (10, 10)) == (2, 3, 6, 7)


def test_clamp_box_extends_past_edges() -> None:
    assert ImageTiles.clamp_box((-4, -1, 12, 15), (10, 8)) == (0, 0, 10, 8)


def test_clamp_box_partial_overlap() -> None:
    assert ImageTiles.clamp_box((-5, 2, 4, 20), (10, 10)) == (0, 2, 4, 10)


def test_clamp_box_on_image_bounds() -> None:
    assert ImageTiles.clamp_box((0, 0, 8, 8), (8, 8)) == (0, 0, 8, 8)


def test_clamp_box_empty_image() -> None:
    assert ImageTiles.clamp_box((-2, 3, 4, 5), (0, 0)) == (0, 0, 0, 0)


def test_clamp_box_outside_collapses_to_edge() -> None:
    assert ImageTiles.clamp_box((12, -4, 20, -1), (10, 8)) == (10, 0, 10, 0)


def test_clamp_box_inverted() -> None:
    with pytest.raises(ValueError, match="Coordinate 'right' is less than 'left'"):
        ImageTiles.clamp_box((6, 1, 2, 5), (10, 10))


def test_clamp_box_inverted_vertically() -> None:
    with pytest.raises(ValueError, match="Coordinate 'lower' is less than 'upper'"):
        ImageTiles.clamp_box((1, 8, 4, 3), (10, 10))


def test_clamp_box_negative_size() -> None:
    with pytest.raises(ValueError, match="image size must be non-negative"):
        ImageTiles.clamp_box((0, 0, 1, 1), (-1, 4))


def test_tile_boxes_exact_division() -> None:
    assert ImageTiles.tile_boxes((8, 6), 2) == [
        (0, 0, 2, 2),
        (2, 0, 4, 2),
        (4, 0, 6, 2),
        (6, 0, 8, 2),
        (0, 2, 2, 4),
        (2, 2, 4, 4),
        (4, 2, 6, 4),
        (6, 2, 8, 4),
        (0, 4, 2, 6),
        (2, 4, 4, 6),
        (4, 4, 6, 6),
        (6, 4, 8, 6),
    ]


def test_tile_boxes_partial_edge() -> None:
    assert ImageTiles.tile_boxes((10, 10), 4) == [
        (0, 0, 4, 4),
        (4, 0, 8, 4),
        (8, 0, 10, 4),
        (0, 4, 4, 8),
        (4, 4, 8, 8),
        (8, 4, 10, 8),
        (0, 8, 4, 10),
        (4, 8, 8, 10),
        (8, 8, 10, 10),
    ]


def test_tile_boxes_odd_tile() -> None:
    assert ImageTiles.tile_boxes((7, 5), 3) == [
        (0, 0, 3, 3),
        (3, 0, 6, 3),
        (6, 0, 7, 3),
        (0, 3, 3, 5),
        (3, 3, 6, 5),
        (6, 3, 7, 5),
    ]


def test_tile_boxes_larger_than_image() -> None:
    assert ImageTiles.tile_boxes((5, 3), 8) == [(0, 0, 5, 3)]


def test_tile_boxes_empty_image() -> None:
    assert ImageTiles.tile_boxes((0, 10), 4) == []
    assert ImageTiles.tile_boxes((10, 0), 4) == []
    assert ImageTiles.tile_boxes((0, 0), 4) == []


def test_tile_boxes_non_positive_tile() -> None:
    with pytest.raises(ValueError, match="tile size must be greater than 0"):
        ImageTiles.tile_boxes((10, 10), 0)
    with pytest.raises(ValueError, match="tile size must be greater than 0"):
        ImageTiles.tile_boxes((10, 10), -2)


def test_tile_boxes_negative_size() -> None:
    with pytest.raises(ValueError, match="image size must be non-negative"):
        ImageTiles.tile_boxes((4, -1), 2)


def test_tile_boxes_cover_every_pixel_once() -> None:
    width, height = 10, 7
    covered = [[0] * width for _ in range(height)]
    for left, upper, right, lower in ImageTiles.tile_boxes((width, height), 3):
        for y in range(upper, lower):
            for x in range(left, right):
                covered[y][x] += 1
    assert all(cell == 1 for row in covered for cell in row)


@pytest.mark.parametrize("mode", ("1", "P", "RGBA"))
def test_tile_boxes_crop(mode: str) -> None:
    im = Image.new(mode, (10, 7))
    boxes = ImageTiles.tile_boxes(im.size, 4)
    crops = [im.crop(box) for box in boxes]
    assert [crop.size for crop in crops] == [
        (4, 4),
        (4, 4),
        (2, 4),
        (4, 3),
        (4, 3),
        (2, 3),
    ]
