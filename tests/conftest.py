import numpy as np
import pytest
from PIL import Image

from camougg.core.service import Service

@pytest.fixture
def service():
    return Service()


@pytest.fixture
def cover_png(tmp_path):
    img = Image.new("RGB", (200, 200), color="white")
    path = tmp_path / "cover.png"
    img.save(path)
    return str(path)


@pytest.fixture
def tiny_cover_png(tmp_path):
    img = Image.new("RGB", (10, 10), color="white")
    path = tmp_path / "tiny_cover.png"
    img.save(path)
    return str(path)


@pytest.fixture
def cover_jpeg(tmp_path):
    rng = np.random.default_rng(seed=42)
    pixels = rng.integers(0, 256, size=(200, 200, 3), dtype=np.uint8)
    img = Image.fromarray(pixels, mode="RGB")
    path = tmp_path / "cover.jpg"
    img.save(path, format="JPEG", quality=90)
    return str(path)


@pytest.fixture
def payload_file(tmp_path):
    path = tmp_path / "secret.txt"
    path.write_bytes(b"My secret message!")
    return str(path)


@pytest.fixture
def empty_payload_file(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_bytes(b"")
    return str(path)
