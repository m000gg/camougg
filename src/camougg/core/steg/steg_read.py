import numpy as np
from camougg.crypto.CSPRN_generator import CSPRNGenerator
from PIL import Image

class StegReader:
    def __init__(self):
        self.generator = CSPRNGenerator()

    def get_num_pixels(self, filepath):
        width, height = Image.open(filepath).size
        return width * height


    def steg_read(self, img_path, password):
        try:
            img = Image.open(img_path)
            img_rgb = img.convert("RGB")
            pixel_array = np.array(img_rgb)
            num_pixels = self.get_num_pixels(img_path)
            if num_pixels < 44:
                raise ValueError("Image is too small to read your message.")


            flat_pixels = pixel_array.reshape(-1, 3)
            shifts = np.arange(8, dtype=np.uint8)
            salt_pixels = flat_pixels[:44]
            salt_pixels_shifted = (salt_pixels[..., np.newaxis] >> shifts) & 1
            lsb_salt_pixels = salt_pixels_shifted[..., 0].flatten()[:128]
            salt = np.packbits(lsb_salt_pixels).tobytes()



            prp = self.generator.hash_password(password, num_pixels - 44, salt)

            prp_shifted = [i + 44 for i in prp]
            chosen_pixels = flat_pixels[prp_shifted]
            bits = (chosen_pixels[..., np.newaxis] >> shifts) & 1
            bitstream = bits[..., 0].flatten()

            weights = 2 ** np.arange(8, dtype=np.uint16)

            res = ""
            total_bits = None
            pos = 0
            reading_header = True

            while reading_header:
                if pos + 8 > bitstream.size:
                    raise ValueError("Invalid password or corrupted image")

                byte_bits = bitstream[pos:(pos + 8)]
                pos += 8

                char_value = int(np.dot(byte_bits, weights))
                text = bytes([char_value]).decode("utf-8", errors="replace")
                res += text

                if text == ">":
                    header_value = res.strip("<>")
                    try:
                        char_count = int(header_value)
                    except ValueError:
                        raise ValueError("Invalid password or corrupted image")

                    total_bits = char_count * 8
                    reading_header = False

                    if total_bits == 0:
                        return ""

            if pos + total_bits > bitstream.size:
                raise ValueError("Invalid password or corrupted image")

            msg_bits = bitstream[pos:pos + total_bits].reshape(-1, 8)
            char_values = msg_bits.dot(weights).astype(np.uint8)

            return "".join(bytes(char_values).decode("utf-8", errors="replace"))

        except (ValueError, OSError, IOError) as e:
            if "Invalid password" in str(e):
                raise
            raise ValueError("Invalid password or corrupted image")