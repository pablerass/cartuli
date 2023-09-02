import cv2 as cv
import logging
import numpy as np

from PIL import Image, ImageOps, ImageDraw

from .measure import Size


def _to_size(value: Size | float | int) -> Size:
    if isinstance(value, float):
        value = round(value)
    if isinstance(value, int):
        value = Size(value, value)
    if isinstance(value, Size):
        value = Size(round(value.width), round(value.height))

    return value


# TODO: Add scale function
# def scale(image: Image.Image, /, ...) -> Image.Image:


def inpaint(image: Image.Image, /, inpaint_size: Size | float | int, image_crop: Size | float | int = 0,
            corner_radius: Size | float | int = 0, inpaint_radius: float | int = 12) -> Image.Image:
    logger = logging.getLogger('cartuli.processing')
    # TODO: Add args dict and/or start trace extra
    logger.debug(f"Start image {image} inpaint", extra={'trace': image})

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
    logger.debug(f"Expand {image} image", extra={'trace': expanded_image})

    mask_image = Image.new('L', (image.size[0] + inpaint_size.width*2,
                                 image.size[1] + inpaint_size.height*2), color='white')
    mask_image_draw = ImageDraw.Draw(mask_image)
    mask_image_draw.rounded_rectangle(
        (inpaint_size.width + image_crop.width, inpaint_size.height + image_crop.height,
         mask_image.size[0] - inpaint_size.width - image_crop.width,
         mask_image.size[1] - inpaint_size.height - image_crop.height),
        fill='black', width=0, radius=max(corner_radius))
    # TUNE: Find a way to round with different vertical and horizontal values
    logger.debug(f"Mask {image} image for inpainting", extra={'trace': mask_image})

    inpaint_image_cv = cv.inpaint(
        cv.cvtColor(np.array(expanded_image), cv.COLOR_RGB2BGR),
        np.array(mask_image), int(inpaint_radius), cv.INPAINT_NS)
    inpainted_image = Image.fromarray(cv.cvtColor(inpaint_image_cv, cv.COLOR_BGR2RGB))
    logger.debug(f"Inpaint {image} image", extra={'trace': inpainted_image})

    return inpainted_image


def _get_rotation_angle(line):
    slope = (line[3] - line[1], line[2] - line[0])
    angle = np.degrees(np.arctan2(*slope))

    # TUNE: There should be some mathematical something to implement this better
    if angle > 90.0:
        angle = angle - 180
    if angle < -90.0:
        angle = angle + 180
    if angle > 45.0:
        return 90 - angle
    if angle < -45.0:
        return -90 - angle
    return angle


def _discard_outliers(data: np.ndarray | list, iqr_scale: float = 1.5) -> np.ndarray:
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    upper_quartile = np.percentile(data, 75)
    lower_quartile = np.percentile(data, 25)
    iqr = upper_quartile - lower_quartile
    scaled_iqr = iqr * iqr_scale
    quartile_set = (lower_quartile - scaled_iqr, upper_quartile + scaled_iqr)
    result_data = []
    for value in data:
        if value >= quartile_set[0] and value <= quartile_set[1]:
            result_data.append(value)
    return result_data


def straighten(image: Image.Image, /, outliers_iqr_scale: float = 0.01) -> Image.Image:
    logger = logging.getLogger('cartuli.processing')
    # TODO: Add args dict and/or start trace extra
    logger.debug(f"Start {image} image straighten", extra={'trace': image})

    # Apply Canny edge detection an detect linkes using Hought Line Transform
    gray_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2GRAY)
    logger.debug(f"Covnert {image} image to gray", extra={'trace': gray_image})
    edges_image = cv.Canny(gray_image, threshold1=50, threshold2=150)
    logger.debug(f"Obtain {image} image edges", extra={'trace': edges_image})
    lines = cv.HoughLinesP(edges_image, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=100)

    # Discard outliers
    line_angles = {tuple(line[0]): _get_rotation_angle(line[0]) for line in lines}
    angles = _discard_outliers(list(line_angles.values()), outliers_iqr_scale)

    # Generate debug image
    image_lines = image.copy()
    image_lines_draw = ImageDraw.Draw(image_lines)
    for line in lines:
        line = tuple(line[0])
        color = "green"
        if line_angles[line] not in angles:
            color = "red"
        image_lines_draw.line((line[0:2], line[2:4]), fill=color, width=2)
    logger.debug(f"Calculate {image} image lines", extra={'trace': image_lines})

    # Calculate the average angle of the detected lines and rotate image
    rotation_angle = -np.mean(angles)
    rotated_image = image.rotate(rotation_angle, expand=False)
    logger.debug(f"Rotate {image} image", extra={'trace': rotated_image})

    # TUNE: Maybe new content generated after rotation should be inpainted

    return rotated_image
