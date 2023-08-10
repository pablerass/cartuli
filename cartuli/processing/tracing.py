from __future__ import annotations

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
    def __init__(self, image: Image.Image | np.ndarray, timestamp: datetime = None, previous: Trace = None, /,
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
        self.__previous = previous

        self.__code = None

    @property
    def image(self) -> Image.Image:
        return self.__image

    @property
    def previous(self) -> Trace:
        return self.__previous

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

    @property
    def code(self) -> str:
        if self.__code is None:
            # TUNE: The code can change during execution
            with Path(self.file_name).open('r') as file:
                file_code = file.readlines()

            last_line = self.line_number
            if self.previous is None or self.function_name != self.previous.function_name:
                # TODO: Add calling function definition
                first_line = last_line - 1
            else:
                first_line = self.previous.line_number
            trace_code_lines = file_code[first_line:last_line]

            # Code formatting or adjustments
            if not trace_code_lines[0].strip():
                del trace_code_lines[0]
            # FIXME: This does not comment lines propery, it should keep align
            # trace_code_lines[-1] = f"# {trace_code_lines[-1]}"

            self.__code = ''.join(trace_code_lines)

        return self.__code


class Tracer:
    def __init__(self):
        self.__traces = []
        self.__last_stream = defaultdict(int)
        # TODO: Add function name and initial file to streams
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

        # TODO: This aproach does not work with multiprocessing
        # TODO: This aproach does not work with loops either
        # TUNE; There must be a more pythonic way of doing this
        stream_number = self.__last_stream[file_name, line_number] + 1
        self.__last_stream[file_name, line_number] = stream_number
        previous_trace = None
        if stream_number in self.__streams:
            previous_trace = self.__streams[stream_number][-1]

        trace = Trace(
            image,
            timestamp,
            previous_trace,
            function_name=function_name,
            file_name=file_name,
            line_number=line_number,
        )

        self.__traces.append(trace)
        self.__streams[stream_number].append(trace)

    def export(self, output_path: Path | str):
        # TODO: Create output by pipeline instead of for all traces
        if output_path is None:
            return

        # TODO: This should be done in a better way
        with output_path.open('w') as output_file:
            output_file.write("""<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.20.0/themes/prism.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.20.0/prism.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.17.1/components/prism-python.min.js"></script>
    </head>
    <body>""")  # TUNE: Homogeneize prism version, I have tried it but this code won't work with all 1.29.0
            for trace in self.__traces:
                image_buffer = io.BytesIO()
                trace.image.save(image_buffer, format="JPEG")
                base64_image = base64.b64encode(image_buffer.getvalue())
                # TODO: Add line numbers in code
                output_file.write(f'<pre><code class="language-python">{trace.code}</code></pre>')
                output_file.write(f'<img src="data:image/jpeg;base64,{base64_image.decode("utf-8")}" />\n<br/>')
            output_file.write("""    </body>
</html>""")

#     def to_notebook(self, output_path: Path | str):
#         nb = nbf.v4.new_notebook()
#
#         initial_image_cell = nbf.v4.new_code_cell()
# image_cell.source = """
# import matplotlib.pyplot as plt
#
# # Load the image
# img = plt.imread('https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Lenna.png/1200px-Lenna.png')
#
# # Display the image
# plt.imshow(img)
# plt.show()
# """
# nb['cells'].append(image_cell)
#
# # Add a code cell that modifies the image
# code_cell = nbf.v4.new_code_cell()
# code_cell.source = """
# import numpy as np
#
# # Convert the image to grayscale
# gray = np.dot(img[...,:3], [0.2989, 0.5870, 0.1140])
#
# # Display the grayscale image
# plt.imshow(gray, cmap='gray')
# plt.show()
# """
# nb['cells'].append(code_cell)
#
# # Save the notebook
# nbf.write(nb, 'my_notebook.ipynb')


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
                file_name=record.pathname,
                line_number=record.lineno
            )
