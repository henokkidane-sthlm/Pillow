.. py:module:: PIL.ImageTiles
.. py:currentmodule:: PIL.ImageTiles

:py:mod:`~PIL.ImageTiles` module
================================

The :py:mod:`~PIL.ImageTiles` module contains helpers for dividing an image into
tiles.

Splitting an image into a grid
------------------------------

::

    from PIL import Image, ImageTiles

    with Image.open("hopper.jpg") as im:
        for index, box in enumerate(ImageTiles.split_grid(im.size, 2, 3)):
            im.crop(box).save(f"tile{index}.png")

Functions
---------

.. autofunction:: PIL.ImageTiles.split_grid
