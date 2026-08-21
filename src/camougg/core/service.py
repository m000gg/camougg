from camougg.core.payload_io import PayloadIO
from camougg.core.steganography import Steganography
from camougg.formats.png_handler import PNGHandler


class Service:

    def __init__(self):
        self.payload_io = PayloadIO()
        self.steganography = Steganography()
        self.png_handler = PNGHandler()

    def embed_file(self, cover_img_path, payload_path, password, output_path):
        data, filename = self.payload_io.read_payload(payload_path)
        flat_pixels, original_shape = self.png_handler.load(cover_img_path)
        modified = self.steganography.steg_write(flat_pixels, password, data, filename)
        self.png_handler.save(modified, original_shape, output_path)

    def extract_file(self, img_path, password, output_dir):
        flat_pixels, original_shape = self.png_handler.load(img_path)
        byte_values, filename = self.steganography.steg_read(flat_pixels, password)
        saved_file_path = self.payload_io.write_payload(byte_values, filename, output_dir)
        return saved_file_path
