import os
import numpy as np
from camougg.crypto.CSPRN_generator import CSPRNGenerator
from PIL import Image, UnidentifiedImageError

class StegWriter:
    def __init__(self):
        self.generator = CSPRNGenerator()

    def get_num_pixels(self, filepath):
        width, height = Image.open(filepath).size
        return width * height

    def steg_write(self, img_path, password, message, output_path="output/output1.png"):
        if not message:
            raise ValueError("Message cannot be empty")

        message = "<{}>{}".format(len(message), message)
        byte_array = np.frombuffer(message.encode("utf-8"), dtype=np.uint8)
        num_pixels = self.get_num_pixels(img_path)

        if num_pixels < 44:
            raise ValueError("Image is too small to hide your message.")

        shifts = np.arange(8, dtype=np.uint8)
        message_bits = (byte_array[:, np.newaxis] >> shifts) & 1

        if message_bits.size > (num_pixels - 44) * 3:
            raise ValueError("Message length exceeds image capacity")

        salt = os.urandom(16)
        prp = self.generator.hash_password(password, num_pixels - 44,salt)
        prp_shifted = [i + 44 for i in prp]

        try:
            img = Image.open(img_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Image not found: {img_path}")
        except UnidentifiedImageError:
            raise ValueError(f"File is not a valid image: {img_path}")

        img_rgb = img.convert("RGB")
        pixel_array = np.array(img_rgb)
        flat_pixels = pixel_array.reshape(-1, 3)

        salt_pixels = flat_pixels[:44]
        salt_pixels_shifted = (salt_pixels[..., np.newaxis] >> shifts) & 1 # [[255, 230, 211]] -> [[11111111, 0100010101 ,10111010]]
        salt_bytes = np.unpackbits(np.frombuffer(salt, dtype=np.uint8)) # [0,1,1,...1]
        flat_lsb = salt_pixels_shifted[..., 0].flatten() # Take the least significant bit for every color
        flat_lsb[:128] = salt_bytes # replace 1st 128 bits with salt bites
        salt_pixels_shifted[..., 0] = flat_lsb.reshape(44, 3) # Reshape to 3D Matrix
        reconstructed_salt_pixels = np.sum(salt_pixels_shifted << shifts, axis=-1).astype(np.uint8) # Make colors from bits
        flat_pixels[:44] = reconstructed_salt_pixels # replace original pixels with "salted" pixels

        prp = prp_shifted[:message_bits.size]

        chosen_pixels = flat_pixels[prp]
        bits = (chosen_pixels[..., np.newaxis] >> shifts) & 1

        flat_msg = message_bits.flatten()
        bits[..., 0].flat[:len(flat_msg)] = flat_msg

        reconstructed_array = np.sum(bits << shifts, axis=-1).astype(np.uint8)
        flat_pixels[prp] = reconstructed_array

        original_shape = pixel_array.shape
        final_img_array = flat_pixels.reshape(original_shape)

        final_img = Image.fromarray(final_img_array)

        try:
            final_img.save(output_path)
        except OSError as ex:
            raise OSError(f"Failed to save output image to {output_path}: {ex}")
