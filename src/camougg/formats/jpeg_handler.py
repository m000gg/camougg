import jpeglib

class JPEGHandler:

    def load(self, cover_img_path):
        try:
            jpeg = jpeglib.read_dct(cover_img_path)
        except OSError:
            raise OSError(f"Failed to read JPEG file: {cover_img_path}")
        return jpeg

    def save(self, jpeg, output_path):
        try:
            jpeg.write_dct(output_path)
        except OSError as ex:
            raise OSError(f"Failed to save output image to {output_path}: {ex}")