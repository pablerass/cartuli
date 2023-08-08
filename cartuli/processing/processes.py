import cv2 as cv
import logging
import numpy as np

from PIL import Image, ImageOps, ImageDraw

from ..measure import Size


def _to_size(value: Size | float | int) -> Size:
    if isinstance(value, float):
        value = round(value)
    if isinstance(value, int):
        value = Size(value, value)
    if isinstance(value, Size):
        value = Size(round(value.width), round(value.height))

    return value


def inpaint(image: Image.Image, /, inpaint_size: Size | float | int, image_crop: Size | float | int = 0,
            corner_radius: Size | float | int = 0, inpaint_radius: float | int = 12) -> Image.Image:
    logger = logging.getLogger('cartuli.processing')
    logger.debug(image)

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
    logger.debug(expanded_image)

    mask_image = Image.new('L', (image.size[0] + inpaint_size.width*2,
                                 image.size[1] + inpaint_size.height*2), color='white')
    mask_image_draw = ImageDraw.Draw(mask_image)
    mask_image_draw.rounded_rectangle(
        (inpaint_size.width + image_crop.width, inpaint_size.height + image_crop.height,
         mask_image.size[0] - inpaint_size.width - image_crop.width,
         mask_image.size[1] - inpaint_size.height - image_crop.height),
        fill='black', width=0, radius=max(corner_radius))
    # TUNE: Find a way to round with different vertical and horizontal values
    logger.debug(mask_image)

    inpaint_image_cv = cv.inpaint(
        cv.cvtColor(np.array(expanded_image), cv.COLOR_RGB2BGR),
        np.array(mask_image), int(inpaint_radius), cv.INPAINT_NS)
    inpainted_image = Image.fromarray(cv.cvtColor(inpaint_image_cv, cv.COLOR_BGR2RGB))
    logger.debug(inpainted_image)

    return inpainted_image


def straighten(image: Image.Image, /) -> Image.Image:
    # TUNE: This code is a mess, it can be ordered for sure
    def get_angle(line):
        # Check if the line is vertical.
        if line[0] == line[2]:
            angle = 90
        else:
            slope = (line[3] - line[1], line[2] - line[0])
            angle = np.degrees(np.arctan2(*slope))

        # Check if the line is horizontal
        if line[1] == line[3]:
            angle = 0

        return angle

    def is_almost_vertical(angle):
        return abs(angle - 90) < 20

    def is_almost_horizontal(angle):
        return abs(angle) < 20

    def vertical_to_rotation(angle):
        return angle - 90

    logger = logging.getLogger('cartuli.processing')
    logger.debug(image)

    # Apply Canny edge detection an detect linkes using Hought Line Transform
    gray_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2GRAY)
    logger.debug(gray_image)
    edges_image = cv.Canny(gray_image, threshold1=50, threshold2=150)
    logger.debug(edges_image)
    lines = cv.HoughLinesP(edges_image, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=100)

    # TUNE: This code is a mess, it can be improved for sure
    image_lines = image.copy()
    image_lines_draw = ImageDraw.Draw(image_lines)
    angles = []
    for line in lines:
        line = line[0]
        angle = get_angle(line)
        color = "red"
        if is_almost_horizontal(angle):
            color = "green"
            angles.append(angle)
        if is_almost_vertical(angle):
            color = "blue"
            angles.append(vertical_to_rotation(angle))
        image_lines_draw.line((tuple(line[0:2]), tuple(line[2:4])), fill=color, width=2)
    logger.debug(image_lines)

    # Calculate the average angle of the detected lines and rotate image
    rotation_angle = -np.mean(angles)
    rotated_image = image.rotate(rotation_angle, expand=True)
    logger.debug(rotated_image)

    return rotated_image
