from __future__ import annotations

import pytest

from PIL import Image, ImageTiles

from .helper import assert_image_equal


def test_even_grid() -> None:
    assert ImageTiles.split_grid((6, 4), 2, 3) == [
        (0, 0, 2, 2),
        (2, 0, 4, 2),
        (4, 0, 6, 2),
        (0, 2, 2, 4),
        (2, 2, 4, 4),
        (4, 2, 6, 4),
    ]


def test_uneven_grid() -> None:
    # 10 / 4 -> widths 2, 3, 2, 3 and 7 / 3 -> heights 2, 2, 3.
    assert ImageTiles.split_grid((10, 7), 3, 4) == [
        (0, 0, 2, 2),
        (2, 0, 5, 2),
        (5, 0, 7, 2),
        (7, 0, 10, 2),
        (0, 2, 2, 4),
        (2, 2, 5, 4),
        (5, 2, 7, 4),
        (7, 2, 10, 4),
        (0, 4, 2, 7),
        (2, 4, 5, 7),
        (5, 4, 7, 7),
        (7, 4, 10, 7),
    ]


def test_single_tile() -> None:
    assert ImageTiles.split_grid((5, 9), 1, 1) == [(0, 0, 5, 9)]


@pytest.mark.parametrize(
    "size, rows, cols",
    (
        ((6, 4), 2, 3),
        ((10, 7), 3, 4),
        ((5, 5), 2, 3),
        ((8, 5), 1, 5),
        ((5, 8), 5, 1),
        ((100, 1), 1, 7),
        ((1, 100), 7, 1),
        ((2, 2), 4, 3),
        ((1, 1), 1, 1),
        ((0, 5), 2, 2),
        ((5, 0), 2, 3),
        ((0, 0), 3, 4),
    ),
)
def test_partition_covers_every_pixel(
    size: tuple[int, int], rows: int, cols: int
) -> None:
    width, height = size
    boxes = ImageTiles.split_grid(size, rows, cols)

    assert len(boxes) == rows * cols

    covered = [[False] * width for _ in range(height)]
    for index, (left, upper, right, lower) in enumerate(boxes):
        row, col = divmod(index, cols)
        assert 0 <= left <= right <= width
        assert 0 <= upper <= lower <= height

        if col == 0:
            assert left == 0
        else:
            previous = boxes[index - 1]
            assert left == previous[2]
            assert (upper, lower) == (previous[1], previous[3])
        if col == cols - 1:
            assert right == width
        if row == 0:
            assert upper == 0
        else:
            above = boxes[index - cols]
            assert upper == above[3]
            assert (left, right) == (above[0], above[2])
        if row == rows - 1:
            assert lower == height

        for y in range(upper, lower):
            for x in range(left, right):
                assert not covered[y][x]
                covered[y][x] = True

    widths = [boxes[col][2] - boxes[col][0] for col in range(cols)]
    heights = [boxes[row * cols][3] - boxes[row * cols][1] for row in range(rows)]
    assert all(pixel for row_covered in covered for pixel in row_covered)
    assert max(widths) - min(widths) <= 1
    assert sum(widths) == width
    assert max(heights) - min(heights) <= 1
    assert sum(heights) == height


def test_crop_reassembles_uneven_image() -> None:
    im = Image.frombytes("L", (10, 7), bytes(range(10 * 7)))
    rebuilt = Image.new("L", im.size)
    for box in ImageTiles.split_grid(im.size, 3, 4):
        rebuilt.paste(im.crop(box), box[:2])
    assert_image_equal(rebuilt, im)


@pytest.mark.parametrize(
    "rows, cols",
    (
        (0, 1),
        (1, 0),
        (0, 0),
        (-1, 2),
        (3, -4),
        (-2, -3),
    ),
)
def test_non_positive_rows_or_cols(rows: int, cols: int) -> None:
    with pytest.raises(ValueError, match="must be positive"):
        ImageTiles.split_grid((8, 8), rows, cols)


def test_negative_size() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        ImageTiles.split_grid((-1, 4), 1, 1)
    with pytest.raises(ValueError, match="non-negative"):
        ImageTiles.split_grid((4, -1), 1, 1)
