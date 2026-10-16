#
# The Python Imaging Library.
#
# tile grid helpers
#
# See the README file for information on usage and redistribution.
#
from __future__ import annotations


def _edges(length: int, parts: int) -> list[int]:
    return [i * length // parts for i in range(parts + 1)]


def split_grid(
    size: tuple[int, int], rows: int, cols: int
) -> list[tuple[int, int, int, int]]:
    """
    Split an image of the given size into a grid of boxes.

    The boxes cover every pixel exactly once. If the width or height does not
    divide evenly, the remainder is spread across the grid, so that tile widths
    (and heights) differ from each other by at most one pixel. If there are more
    rows or columns than pixels, some boxes will be empty.

    :param size: The image size, as a 2-tuple: (width, height).
    :param rows: The number of rows in the grid.
    :param cols: The number of columns in the grid.
    :returns: A list of ``rows * cols`` (left, upper, right, lower) boxes, in
              row-major order. These can be passed to
              :py:meth:`~PIL.Image.Image.crop`.
    :exception ValueError: If ``rows`` or ``cols`` is not positive, or if
                           ``size`` is negative.
    """
    if rows <= 0 or cols <= 0:
        msg = "rows and cols must be positive"
        raise ValueError(msg)
    width, height = size
    if width < 0 or height < 0:
        msg = "width and height must be non-negative"
        raise ValueError(msg)

    xs = _edges(width, cols)
    ys = _edges(height, rows)
    return [
        (xs[c], ys[r], xs[c + 1], ys[r + 1]) for r in range(rows) for c in range(cols)
    ]
