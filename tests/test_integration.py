import pytest
from pathlib import Path
from PIL import Image
import numpy as np

class TestPngEmbedExtract:

    def test_embed_then_extract_recovers_original_bytes_and_filename(
            self, service, cover_png, payload_file, tmp_path
    ):
        output_image = tmp_path / "stego.png"
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()

        service.embed_file(cover_png, payload_file, "correct_password", str(output_image))
        saved_path = service.extract_file(str(output_image), "correct_password", str(extract_dir))

        assert Path(saved_path).read_bytes() == Path(payload_file).read_bytes()
        assert Path(saved_path).name == Path(payload_file).name

    def test_wrong_password_raises_generic_error(
            self, service, cover_png, payload_file, tmp_path
    ):
        output_image = tmp_path / "stego.png"
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()

        service.embed_file(cover_png, payload_file, "correct_password", str(output_image))

        with pytest.raises(ValueError, match="Invalid password or corrupted image"):
            service.extract_file(str(output_image), "wrong_password", str(extract_dir))

    def test_corrupted_salt_zone_raises_generic_error(
            self, service, cover_png, payload_file, tmp_path
    ):
        output_image = tmp_path / "stego.png"
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()

        service.embed_file(cover_png, payload_file, "correct_password", str(output_image))

        img = Image.open(output_image).convert("RGB")
        pixels = np.array(img)
        flat = pixels.reshape(-1, 3)
        flat[:44] = flat[:44] ^ 1  # flip the LSB of every channel in the salt zone
        Image.fromarray(flat.reshape(pixels.shape)).save(output_image)

        with pytest.raises(ValueError, match="Invalid password or corrupted image"):
            service.extract_file(str(output_image), "correct_password", str(extract_dir))

    def test_oversized_payload_rejected_before_writing(
            self, service, tiny_cover_png, tmp_path
    ):
        oversized_payload = tmp_path / "big.bin"
        oversized_payload.write_bytes(b"\x00" * 5000)
        output_image = tmp_path / "stego.png"

        with pytest.raises(ValueError, match="capacity"):
            service.embed_file(str(tiny_cover_png), str(oversized_payload), "password", str(output_image))

        assert not output_image.exists()

    def test_embed_empty_payload_raises(self, service, cover_png, empty_payload_file, tmp_path):
        output_image = tmp_path / "stego.png"
        with pytest.raises(ValueError):
            service.embed_file(cover_png, empty_payload_file, "password", str(output_image))

    def test_embed_nonexistent_cover_image_raises(self, service, payload_file, tmp_path):
        output_image = tmp_path / "stego.png"
        with pytest.raises(FileNotFoundError):
            service.embed_file(
                str(tmp_path / "does_not_exist.png"), payload_file, "password", str(output_image)
            )

    def test_embed_nonexistent_payload_file_raises(self, service, cover_png, tmp_path):
        output_image = tmp_path / "stego.png"
        with pytest.raises(FileNotFoundError):
            service.embed_file(
                cover_png, str(tmp_path / "does_not_exist.txt"), "password", str(output_image)
            )


class TestJpegEmbedExtract:

    def test_embed_then_extract_recovers_original_bytes_and_filename(
            self, service, cover_jpeg, payload_file, tmp_path
    ):
        output_image = tmp_path / "stego.jpg"
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()

        service.embed_file(cover_jpeg, payload_file, "correct_password", str(output_image))
        saved_path = service.extract_file(str(output_image), "correct_password", str(extract_dir))

        assert Path(saved_path).read_bytes() == Path(payload_file).read_bytes()
        assert Path(saved_path).name == Path(payload_file).name

    def test_wrong_password_raises_generic_error(
            self, service, cover_jpeg, payload_file, tmp_path
    ):
        output_image = tmp_path / "stego.jpg"
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()

        service.embed_file(cover_jpeg, payload_file, "correct_password", str(output_image))

        with pytest.raises(ValueError, match="Invalid password or corrupted image"):
            service.extract_file(str(output_image), "wrong_password", str(extract_dir))