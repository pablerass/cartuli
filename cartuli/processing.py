import numpy as np

import cv2 as cv

from PIL import Image, ImageOps, ImageDraw

from .measure import Size


def __to_size(value: Size | float | int) -> Size:
    if isinstance(value, float):
        value = round(value)
    if isinstance(value, int):
        value = Size(value, value)
    if isinstance(value, Size):
        value = Size(round(value.width), round(value.height))

    return value


def inpaint(image: Image.Image, inpaint_size: Size | float | int, image_crop: Size | float | int = 0,
            corner_radius: Size | float | int = 0) -> Image.Image:
    inpaint_size = __to_size(inpaint_size)
    image_crop = __to_size(image_crop)
    corner_radius = __to_size(corner_radius)

    expand_size = max(inpaint_size)
    expand_crop = Size(expand_size - inpaint_size.width, expand_size - inpaint_size.height)
    expanded_image = ImageOps \
        .expand(image, border=expand_size, fill='white') \
        .crop((expand_crop.width, expand_crop.height,
               image.size[0] + expand_size*2 - expand_crop.width,
               image.size[1] + expand_size*2 - expand_crop.height))

    mask_image = Image.new('L', (image.size[0] + inpaint_size.width*2,
                                 image.size[1] + inpaint_size.height*2), color='white')
    mask_image_draw = ImageDraw.Draw(mask_image)
    mask_image_draw.rounded_rectangle(
        (inpaint_size.width + image_crop.width, inpaint_size.height + image_crop.height,
         mask_image.size[0] - inpaint_size.width - image_crop.width,
         mask_image.size[1] - inpaint_size.height - image_crop.height),
        fill='black', width=0, radius=max(corner_radius))
    # TUNE: Find a way to round with different vertical and horizontal values

    inpaint_image_cv = cv.inpaint(
        cv.cvtColor(np.array(expanded_image), cv.COLOR_RGB2BGR), np.array(mask_image), 15, cv.INPAINT_NS)

    return Image.fromarray(cv.cvtColor(inpaint_image_cv, cv.COLOR_BGR2RGB))
