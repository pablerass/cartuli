import base64
import io

from abc import ABC, abstractmethod
from pathlib import Path

from .trace import Trace


class TraceOutput(ABC):
    def __init__(self, traces: list[Trace]):
        self._traces = traces

    @property
    def traces(self) -> tuple[Trace]:
        return tuple(self._tracer)

    @abstractmethod
    def create(self, output_dir: Path | str):
        pass


class TraceHTMLOutput(TraceOutput):
    def create(self, output_dir: Path | str):
        PRISM_VERSION = "1.29.0"
        PRISM_URL = f"https://cdnjs.cloudflare.com/ajax/libs/prism/{PRISM_VERSION}"

        BOOTSTRAP_VERSION = "5.2.3"
        BOOTSTRAP_URL = f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist"

        if isinstance(output_dir, str):
            output_dir = Path(output_dir)

        # TODO: This is a bad way to avoid errors when no path is specified
        if output_dir is None:
            return

        with output_dir.open('w') as output_file:
            output_file.write(f"""<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="{BOOTSTRAP_URL}/css/bootstrap.min.css" />
        <link rel="stylesheet" href="{PRISM_URL}/themes/prism.min.css" />
        <script src="{BOOTSTRAP_URL}/js/bootstrap.min.js"></script>
        <script src="{BOOTSTRAP_URL}/js/bootstrap.bundle.min.js"></script>
        <script src="{PRISM_URL}/prism.min.js"></script>
        <script src="{PRISM_URL}/components/prism-python.min.js"></script>
    </head>
    <body>""")
            output_file.write(f"""
        <ul class="nav nav-tabs mb-{len(self._traces)}" id="ex1" role="tablist">""")
            for n, trace in enumerate(self._traces):
                output_file.write(f"""
            <li class="nav-item" role="presentation">
                <a class="nav-link{ " active" if not n else ""}"
                   id="ex1-tab-{n+1}"
                   data-mdb-toggle="tab"
                   href="#ex1-tabs-{n+1}"
                   role="tab"
                   aria-controls="ex1-tabs-{n+1}"
                   aria-selected="{"true" if not n else "false"}">{trace.image_file.relative_to(Path.cwd())}
                </a>
            </li>""")
            output_file.write("""
        </ul>
        <div class="tab-content" id="ex1-content">""")
            for n, trace in enumerate(self._traces):
                output_file.write(f"""
            <div class="tab-pane fade{ " show active" if not n else ""}"
                 id="ex1-tabs-{n+1}"
                 role="tabpanel"
                 aria-labelledby="ex1-tab-{n+1}">""")
                for record in trace:
                    image_buffer = io.BytesIO()
                    record.image.save(image_buffer, format="JPEG")
                    base64_image = base64.b64encode(image_buffer.getvalue())
                    # TODO: Add line numbers in code, this approach does not work
                    output_file.write(f"""
                <pre><code class="language-python line-numbers">{record.code}</code></pre>
                <img src="data:image/jpeg;base64,{base64_image.decode("utf-8")}" />
                <br/>""")
            output_file.write("""
        </div>""")
            output_file.write("""
    </body>
</html>""")


class TraceNotebookOutput(TraceOutput):
    def create(self, output_dir: Path | str):
        pass
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
