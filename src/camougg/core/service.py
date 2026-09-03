from camougg.core.payload_io import PayloadIO
from camougg.core.steganography import Steganography
from camougg.formats.png_handler import PNGHandler
from camougg.formats.jpeg_handler import JPEGHandler
import os


class Service:

    def __init__(self):
        self.payload_io = PayloadIO()
        self.steganography = Steganography()
        self.png_handler = PNGHandler()
        self.jpeg_handler = JPEGHandler()

    def embed_file(self, cover_img_path, payload_path, password, output_path):
        data, filename = self.payload_io.read_payload(payload_path)
        extension = os.path.splitext(cover_img_path)[1].lower()

        if extension in (".jpg", ".jpeg"):
            jpeg = self.jpeg_handler.load(cover_img_path)
            modified_Y = self.steganography.steg_write_dct(jpeg.Y, password, data, filename)
            jpeg.Y = modified_Y
            self.jpeg_handler.save(jpeg, output_path)
        else:
            flat_pixels, original_shape = self.png_handler.load(cover_img_path)
            modified = self.steganography.steg_write(flat_pixels, password, data, filename)
            self.png_handler.save(modified, original_shape, output_path)

    def extract_file(self, img_path, password, output_dir):
        extension = os.path.splitext(img_path)[1].lower()

        if extension in (".jpg", ".jpeg"):
            jpeg = self.jpeg_handler.load(img_path)
            data, filename = self.steganography.steg_read_dct(jpeg.Y, password)
        else:
            flat_pixels, original_shape = self.png_handler.load(img_path)
            data, filename = self.steganography.steg_read(flat_pixels, password)

        saved_file_path = self.payload_io.write_payload(data, filename, output_dir)
        return saved_file_path
