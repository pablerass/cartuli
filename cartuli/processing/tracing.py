import cv2 as cv
import inspect
import numpy as np
import re

from datetime import datetime
from logging import Handler, LogRecord, NOTSET
from pathlib import Path
from PIL import Image


PERSIST_REGEX = re.compile(r"^\s*_persist\((?P<name>\w+)\s*,.*$")


class Trace:
    # TUNE: This could be applied to any type of object
    def __init__(self, image: Image.Image | np.ndarray, timestamp: datetime = None, /,
                 function_name: str = None, file_name: str = None, line_number: int = None):
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        self.__image = image.copy()

        if timestamp is None:
            timestamp = datetime.now()
        self.__timestamp = timestamp

        self.__function_name = function_name
        self.__file_name = file_name
        self.__line_number = line_number

    @property
    def image(self) -> Image.Image:
        return self.__image

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    @property
    def function_name(self) -> str | None:
        return self.__function_name

    @property
    def file_name(self) -> str | None:
        return self.__file_name

    @property
    def line_number(self) -> int | None:
        return self.__line_number


class Tracer:
    def __init__(self):
        self.__traces = []

    @property
    def traces(self) -> tuple[dict]:
        return tuple(self.__traces)

    def record(self, image: Image.Image | np.ndarray, /, timestamp: datetime = None,
               function_name: str = None, file_name: str = None, line_number: int = None) -> None:
        # TUNE: I tried to move arroung frame info but logging does not return it
        # maybe there is a better way
        if function_name is None or file_name is None or line_number is None:
            calling_frame = inspect.currentframe().f_back
            calling_frame_info = inspect.getframeinfo(calling_frame)
            function_name = calling_frame_info.function
            file_name = calling_frame_info.filename
            line_number = calling_frame_info.lineno

        self.__traces.append(
            Trace(image,
                  timestamp,
                  function_name=function_name,
                  file_name=file_name,
                  line_number=line_number))


class ImageHandler(Handler):
    def __init__(self, tracer: Tracer, level=NOTSET):
        self.__tracer = tracer
        super().__init__(level)

    def emit(self, record: LogRecord) -> None:
        images = []
        timestamp = datetime.fromtimestamp(record.created)

        # Register only the first found image
        if isinstance(record.msg, Image.Image) or isinstance(record.msg, np.ndarray):
            images.append(record.msg)
        for arg in record.args:
            if isinstance(arg, Image.Image) or isinstance(arg, np.ndarray):
                images.append(arg)

        for image in images:
            self.__tracer.record(
                image,
                timestamp=timestamp,
                function_name=record.funcName,
                file_name=record.filename,
                line_number=record.lineno
            )


def _persist(image: Image.Image | np.ndarray, dir_path: Path | str = None) -> None:
    # TUNE: Make this use logging levels to manage debug images creation
    # TUNE: This coluld be part of an image processing logging class
    if dir_path is not None:
        calling_line = inspect.getframeinfo(inspect.currentframe().f_back).code_context[0]
        name = PERSIST_REGEX.match(calling_line)['name']
        if isinstance(dir_path, str):
            dir_path = Path(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        image_path = dir_path / f'{datetime.now().strftime("%Y%M%d%H%M%s")}-{name}.png'
        if isinstance(image, Image.Image):
            image.save(image_path)
        elif isinstance(image, np.ndarray):
            cv.imwrite(str(image_path), image)
        else:
            raise AttributeError(f'Invalid image type {type(image)}')
