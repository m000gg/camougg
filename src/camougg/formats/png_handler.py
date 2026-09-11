from PIL import Image, UnidentifiedImageError
import numpy as np

class PNGHandler():

    def get_num_pixels(self, filepath):
        width, height = Image.open(filepath).size
        return width * height

    def load(self, img_path) -> tuple[np.ndarray, tuple]:
        try:
            img = Image.open(img_path)
            img_rgb = img.convert("RGB")
            pixel_array = np.array(img_rgb)
            original_shape = pixel_array.shape
            flat_pixels = pixel_array.reshape(-1, 3)
            return flat_pixels, original_shape
        except FileNotFoundError:
            raise FileNotFoundError(f"Image not found: {img_path}")
        except UnidentifiedImageError:
            raise ValueError(f"File is not a valid image: {img_path}")

    def save(self, flat_pixels, original_shape, output_path) -> None:
        final_img_array = flat_pixels.reshape(original_shape)
        final_img = Image.fromarray(final_img_array)

        try:
            final_img.save(output_path)
        except OSError as ex:
            raise OSError(f"Failed to save output image to {output_path}: {ex}")