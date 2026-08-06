import pytest
from pathlib import Path
from PIL import Image
from camougg.core.steg.steg_write import StegWriter

@pytest.fixture
def test_image(tmp_path):
    img = Image.new('RGB', (200, 200), color='white')
    img_path = tmp_path / "test.png"
    img.save(img_path)
    return str(img_path)

@pytest.fixture
def large_test_image(tmp_path):
    img = Image.new('RGB', (2000, 2000), color='white')
    img_path = tmp_path / "large_test.png"
    img.save(img_path)
    return str(img_path)

@pytest.fixture
def embedded_image(test_image, tmp_path):
    output = tmp_path / "embedded.png"
    writer = StegWriter()
    writer.steg_write(test_image, "correct_password", "expected_secret", str(output))
    return str(output)