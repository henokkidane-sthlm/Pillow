.. py:module:: PIL.ImageTiles
.. py:currentmodule:: PIL.ImageTiles

:py:mod:`~PIL.ImageTiles` module
================================

The :py:mod:`~PIL.ImageTiles` module splits an image size into a grid of crop
boxes.

::

    from PIL import Image, ImageTiles

    with Image.open("hopper.jpg") as im:
        for box in ImageTiles.split_grid(im.size, 2, 3):
            tile = im.crop(box)

Functions
---------

.. autofunction:: PIL.ImageTiles.split_grid
