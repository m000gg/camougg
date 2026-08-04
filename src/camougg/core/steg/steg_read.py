import numpy as np
from src.camougg.crypto.CSPRNGenerator import CSPRNGenerator
from PIL import Image

class StegReader:
    def __init__(self):
        self.generator = CSPRNGenerator()

    def get_num_pixels(self, filepath):
        width, height = Image.open(filepath).size
        return width * height


    def steg_read(self, img_path, password):
        img = Image.open(img_path)
        img_rgb = img.convert("RGB")
        pixel_array = np.array(img_rgb)
        num_pixels = self.get_num_pixels(img_path)
        prp = self.generator.hash_password(password, num_pixels)

        flat_pixels = pixel_array.reshape(-1, 3)
        shifts = np.arange(8, dtype=np.uint8)

        chosen_pixels = flat_pixels[prp]  # (N, 3)
        bits = (chosen_pixels[..., np.newaxis] >> shifts) & 1  # (N, 3, 8)
        bitstream = bits[..., 0].flatten()  # (N*3,)

        weights = 2 ** np.arange(8, dtype=np.uint16)  # bit0..bit7 = LSB..MSB

        res = ""
        total_bits = None
        pos = 0

        reading_header = True

        while reading_header:
            if pos + 8 > bitstream.size:
                raise ValueError(
                    "Could not find message header end — wrong password or corrupted image"
                )

            byte_bits = bitstream[pos:(pos + 8)]  # take 1st 8 bits
            pos += 8

            char_value = int(np.dot(byte_bits, weights))
            text = bytes([char_value]).decode("utf-8", errors="replace")
            res += text

            if text == ">":
                header_value = res.strip("<>")
                try:
                    char_count = int(header_value)
                except ValueError:
                    raise ValueError(
                        "Failed to parse message header — wrong password or corrupted image"
                    )

                total_bits = char_count * 8
                reading_header = False

                if total_bits == 0:
                    return ""

        if pos + total_bits > bitstream.size:
            raise ValueError(
                "Could not extract full message — wrong password, corrupted image, or message longer than container"
            )

        msg_bits = bitstream[pos:pos + total_bits].reshape(-1, 8)  # (num_chars, 8)
        char_values = msg_bits.dot(weights).astype(np.uint8)  # (num_chars,)

        return bytes(char_values.tolist()).decode("utf-8", errors="replace")