import pytest
from PIL import Image
from camougg.core.steg.steg_write import StegWriter
from camougg.crypto.CSPRNGenerator import CSPRNGenerator


class TestStegWriter:
    @pytest.fixture
    def test_image(self, tmp_path):
        img = Image.new('RGB', (100, 100), color='white')
        img_path = tmp_path / "test.png"
        img.save(img_path)
        return str(img_path)

    def test_embed_simple_message(self, test_image, tmp_path):
        writer = StegWriter()
        output = tmp_path / "output.png"

        writer.steg_write(test_image, "password123", "Hello", str(output))

        assert output.exists()

    def test_embed_empty_message(self, test_image, tmp_path):
        writer = StegWriter()
        output = tmp_path / "output.png"

        with pytest.raises(ValueError):
            writer.steg_write(test_image, "password123", "", str(output))

    def test_embed_nonexistent_image(self, tmp_path):
        writer = StegWriter()

        with pytest.raises(Exception):
            writer.steg_write("/nonexistent/image.png", "pass", "secret", str(tmp_path / "out.png"))