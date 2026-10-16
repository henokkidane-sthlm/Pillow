"""
Split an image size into a grid of crop boxes.
"""

from __future__ import annotations


def _boundaries(length: int, parts: int) -> list[int]:
    """Return the ``parts + 1`` edges of an even partition of ``length``.

    Boundaries fall at ``i * length // parts``. Part sizes differ by at most
    one, and any remainder pixels are spaced along the axis instead of being
    grouped at one end.
    """
    return [i * length // parts for i in range(parts + 1)]


def split_grid(
    size: tuple[int, int], rows: int, cols: int
) -> list[tuple[int, int, int, int]]:
    """
    Split an image size into a ``rows`` by ``cols`` grid of crop boxes.

    :param size: The image size, as a ``(width, height)`` tuple.
    :param rows: Number of rows. Must be greater than zero.
    :param cols: Number of columns. Must be greater than zero.
    :returns: ``rows * cols`` boxes, ``(left, upper, right, lower)``, in
        row-major order. The boxes are suitable for
        :py:meth:`~PIL.Image.Image.crop` and cover every pixel of ``size``
        exactly once. When ``width`` or ``height`` is not divisible by
        ``cols`` or ``rows``, remainder pixels are spread so that tile sizes
        along that axis differ by at most one.
    :raises ValueError: If ``rows`` or ``cols`` is not positive, or if a
        dimension of ``size`` is negative.
    """
    if rows <= 0:
        msg = "rows must be positive"
        raise ValueError(msg)
    if cols <= 0:
        msg = "cols must be positive"
        raise ValueError(msg)

    width, height = size
    if width < 0 or height < 0:
        msg = "size dimensions must be non-negative"
        raise ValueError(msg)

    xs = _boundaries(width, cols)
    ys = _boundaries(height, rows)
    return [
        (xs[col], ys[row], xs[col + 1], ys[row + 1])
        for row in range(rows)
        for col in range(cols)
    ]
