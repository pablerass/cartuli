import base64
import cv2 as cv
import inspect
import io
import numpy as np

from collections import defaultdict
from datetime import datetime
from logging import Handler, LogRecord, NOTSET
from pathlib import Path
from PIL import Image


class Trace:
    # TUNE: This could be applied to any type of object
    def __init__(self, image: Image.Image | np.ndarray, timestamp: datetime = None, /,
                 function_name: str = None, file_name: str = None, line_number: int = None):
        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB))
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
        self.__last_stream = defaultdict(int)
        self.__streams = defaultdict(list)

    @property
    def traces(self) -> tuple[dict]:
        return tuple(self.__traces)

    @property
    def streams(self) -> dict[int, tuple[dict]]:
        return {k: tuple(v) for k, v in self.__streams.items()}

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

        trace = Trace(
            image,
            timestamp,
            function_name=function_name,
            file_name=file_name,
            line_number=line_number
        )

        # TODO: This aproach does not work with multiprocessing
        # TUNE; There must be a more pythonic way of doing this
        stream_number = self.__last_stream[file_name, line_number] + 1
        self.__last_stream[file_name, line_number] = stream_number
        self.__traces.append(trace)
        self.__streams[stream_number].append(trace)

    def export(self, output_path: Path | str):
        if output_path is None:
            return

        with output_path.open('w') as output_file:
            for trace in self.__traces:
                image_buffer = io.BytesIO()
                trace.image.save(image_buffer, format="JPEG")
                base64_image = base64.b64encode(image_buffer.getvalue())
                output_file.write(f'<img src="data:image/jpeg;base64,{base64_image.decode("utf-8")}" />\n</br>')

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
