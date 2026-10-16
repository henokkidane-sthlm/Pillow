from __future__ import annotations

import pytest

from PIL import Image, ImageTiles

from .helper import assert_image_equal, hopper


def assert_exact_cover(
    size: tuple[int, int], boxes: list[tuple[int, int, int, int]]
) -> None:
    width, height = size
    counts = [[0] * width for _ in range(height)]
    for left, upper, right, lower in boxes:
        assert 0 <= left <= right <= width
        assert 0 <= upper <= lower <= height
        for y in range(upper, lower):
            for x in range(left, right):
                counts[y][x] += 1
    assert all(count == 1 for row in counts for count in row)


def test_even() -> None:
    assert ImageTiles.split_grid((4, 6), 3, 2) == [
        (0, 0, 2, 2),
        (2, 0, 4, 2),
        (0, 2, 2, 4),
        (2, 2, 4, 4),
        (0, 4, 2, 6),
        (2, 4, 4, 6),
    ]


def test_single_tile() -> None:
    assert ImageTiles.split_grid((7, 5), 1, 1) == [(0, 0, 7, 5)]


def test_uneven() -> None:
    assert ImageTiles.split_grid((10, 5), 2, 3) == [
        (0, 0, 3, 2),
        (3, 0, 6, 2),
        (6, 0, 10, 2),
        (0, 2, 3, 5),
        (3, 2, 6, 5),
        (6, 2, 10, 5),
    ]


@pytest.mark.parametrize(
    "size, rows, cols",
    (
        ((10, 10), 3, 3),
        ((11, 7), 4, 3),
        ((100, 37), 7, 9),
        ((1, 13), 5, 1),
        ((13, 1), 1, 5),
        ((3, 2), 4, 5),
        ((0, 0), 2, 2),
    ),
)
def test_exact_cover(size: tuple[int, int], rows: int, cols: int) -> None:
    boxes = ImageTiles.split_grid(size, rows, cols)

    assert len(boxes) == rows * cols
    assert_exact_cover(size, boxes)


@pytest.mark.parametrize(
    "size, rows, cols",
    (
        ((10, 10), 3, 3),
        ((101, 53), 7, 9),
        ((17, 4), 1, 16),
    ),
)
def test_remainder_spread_evenly(size: tuple[int, int], rows: int, cols: int) -> None:
    boxes = ImageTiles.split_grid(size, rows, cols)

    widths = {right - left for left, _, right, _ in boxes}
    heights = {lower - upper for _, upper, _, lower in boxes}
    assert max(widths) - min(widths) <= 1
    assert max(heights) - min(heights) <= 1


def test_row_major_order() -> None:
    boxes = ImageTiles.split_grid((9, 8), 4, 3)

    assert boxes == sorted(boxes, key=lambda box: (box[1], box[0]))
    for r in range(4):
        row = boxes[r * 3 : r * 3 + 3]
        assert len({box[1] for box in row}) == 1


def test_reassemble() -> None:
    im = hopper()
    out = Image.new(im.mode, im.size)
    for box in ImageTiles.split_grid(im.size, 5, 7):
        out.paste(im.crop(box), box[:2])

    assert_image_equal(out, im)


@pytest.mark.parametrize("rows, cols", ((0, 1), (1, 0), (-1, 2), (2, -3), (0, 0)))
def test_invalid_grid(rows: int, cols: int) -> None:
    with pytest.raises(ValueError, match="rows and cols must be positive"):
        ImageTiles.split_grid((10, 10), rows, cols)


@pytest.mark.parametrize("size", ((-1, 10), (10, -1)))
def test_invalid_size(size: tuple[int, int]) -> None:
    with pytest.raises(ValueError, match="width and height must be non-negative"):
        ImageTiles.split_grid(size, 2, 2)
