import cv2 as cv
import numpy as np

from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

from ..measure import Size
from .tracing import _persist


def _to_size(value: Size | float | int) -> Size:
    if isinstance(value, float):
        value = round(value)
    if isinstance(value, int):
        value = Size(value, value)
    if isinstance(value, Size):
        value = Size(round(value.width), round(value.height))

    return value


def inpaint(image: Image.Image, /, inpaint_size: Size | float | int, image_crop: Size | float | int = 0,
            corner_radius: Size | float | int = 0, inpaint_radius: float | int = 12,
            debug_dir: Path | str = None) -> Image.Image:
    _persist(image, debug_dir)
    inpaint_size = _to_size(inpaint_size)
    image_crop = _to_size(image_crop)
    corner_radius = _to_size(corner_radius)

    expand_size = max(inpaint_size)
    expand_crop = Size(expand_size - inpaint_size.width, expand_size - inpaint_size.height)
    expanded_image = ImageOps \
        .expand(image, border=expand_size, fill='white') \
        .crop((expand_crop.width, expand_crop.height,
               image.size[0] + expand_size*2 - expand_crop.width,
               image.size[1] + expand_size*2 - expand_crop.height))
    _persist(expanded_image, debug_dir)

    mask_image = Image.new('L', (image.size[0] + inpaint_size.width*2,
                                 image.size[1] + inpaint_size.height*2), color='white')
    mask_image_draw = ImageDraw.Draw(mask_image)
    mask_image_draw.rounded_rectangle(
        (inpaint_size.width + image_crop.width, inpaint_size.height + image_crop.height,
         mask_image.size[0] - inpaint_size.width - image_crop.width,
         mask_image.size[1] - inpaint_size.height - image_crop.height),
        fill='black', width=0, radius=max(corner_radius))
    # TUNE: Find a way to round with different vertical and horizontal values
    _persist(mask_image, debug_dir)

    inpaint_image_cv = cv.inpaint(
        cv.cvtColor(np.array(expanded_image), cv.COLOR_RGB2BGR),
        np.array(mask_image), int(inpaint_radius), cv.INPAINT_NS)
    _persist(inpaint_image_cv, debug_dir)

    inpainted_image = Image.fromarray(cv.cvtColor(inpaint_image_cv, cv.COLOR_BGR2RGB))
    _persist(inpainted_image, debug_dir)

    return inpainted_image


def straighten(image: Image.Image, /, debug_dir: Path | str = None) -> Image.Image:
    _persist(image, debug_dir)

    # Apply Canny edge detection an detect linkes using Hought Line Transform
    gray_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2GRAY)
    _persist(gray_image, debug_dir)
    edges = cv.Canny(gray_image, threshold1=50, threshold2=200)
    _persist(edges, debug_dir)
    lines = cv.HoughLinesP(edges, 1, np.pi/180, threshold=150, minLineLength=None, maxLineGap=None)
    _persist(lines, debug_dir)

    # Calculate the average angle of the detected lines and rotate image
    angles = [np.arctan2(line[0][3] - line[0][1], line[0][2] - line[0][0]) for line in lines]
    angle_degrees = np.degrees(np.mean(angles))
    rotated_image = image.copy().rotate(angle_degrees, expand=True)
    _persist(rotated_image, debug_dir)

    return rotated_image
