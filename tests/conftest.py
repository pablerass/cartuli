import pytest

import os
import random
import shutil
import tempfile

from pathlib import Path
from PIL import Image


from cartuli.card import CardImage
from cartuli.measure import Size, STANDARD



TEST_PATH = Path(__file__).resolve().parent
TEST_FILES_PATH = Path(__file__).resolve().parent / "files"


@pytest.fixture
def fixture_file() -> Path:
    def path(rel_path: Path | str):
        return TEST_FILES_PATH / rel_path

    return path


@pytest.fixture
def fixture_content() -> str:
    def path(rel_path: Path | str):
        return (TEST_FILES_PATH / rel_path).read_text()

    return path


@pytest.fixture
def random_image() -> Image.Image:
    def create_image(size: Size = None):
        aspect_ratio = random.choice([(3, 2), (4, 3)])
        if size is None:
            width = random.randint(300, 1000)
            height = int(width * aspect_ratio[1] / aspect_ratio[0])
        else:
            width = int(size.width)
            height = int(size.height)

        return Image.new('RGB', (width, height), color=(255, 0, 0))

    return create_image


@pytest.fixture
def random_image_file(random_image) -> Path:
    temp_dir = Path(tempfile.mkdtemp())

    def create_temp_file(subpath: Path = None, /, size: Size = None):
        file_name = f"{next(tempfile._get_candidate_names())}.png"
        if subpath:
            full_subpath = temp_dir / subpath
            full_subpath.mkdir(parents=True, exist_ok=True)
            temp_file = full_subpath / file_name
        else:
            temp_file = temp_dir / file_name

        random_image(size).save(temp_file)

        return temp_file

    yield create_temp_file

    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def random_card_image(random_image) -> CardImage:
    def create_temp_card_image(subpath: Path = None, /, size: Size = STANDARD):
        return CardImage(random_image(subpath), size=size)

    return create_temp_card_image