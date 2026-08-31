import numpy as np
from camougg.crypto.CSPRN_generator import CSPRNGenerator
import os
import jpeglib


class Steganography:
    def __init__(self):
        self.generator = CSPRNGenerator()

    def steg_read(self, flat_pixels, password):
        try:
            shifts = np.arange(8, dtype=np.uint8)
            salt_pixels = flat_pixels[:44]
            salt_pixels_shifted = (salt_pixels[..., np.newaxis] >> shifts) & 1
            lsb_salt_pixels = salt_pixels_shifted[..., 0].flatten()[:128]
            salt = np.packbits(lsb_salt_pixels).tobytes()

            num_pixels = flat_pixels.shape[0]
            prp = self.generator.hash_password(password, num_pixels - 44, salt)

            prp_shifted = [i + 44 for i in prp]
            chosen_pixels = flat_pixels[prp_shifted]
            bits = (chosen_pixels[..., np.newaxis] >> shifts) & 1
            bitstream = bits[..., 0].flatten()

            weights = 2 ** np.arange(8, dtype=np.uint16)
            pos = 0

            def read_next_byte():
                nonlocal pos
                if pos + 8 > bitstream.size:
                    raise ValueError("Invalid password or corrupted image")
                byte_bits = bitstream[pos:pos + 8]
                pos += 8
                return int(np.dot(byte_bits, weights))

            if read_next_byte() != ord('<'):
                raise ValueError("Invalid password or corrupted image")

            length_bytes = bytearray()
            while True:
                b = read_next_byte()
                if b == ord('|'):
                    break
                length_bytes.append(b)
            try:
                file_size_bytes = int(length_bytes.decode('ascii'))
            except ValueError:
                raise ValueError("Invalid password or corrupted image")

            total_bits = file_size_bytes * 8

            filename_bytes = bytearray()
            while True:
                b = read_next_byte()
                if b == ord('>'):
                    break
                filename_bytes.append(b)

            filename = filename_bytes.decode('utf-8', errors='replace')

            if total_bits == 0:
                return b"", filename

            if pos + total_bits > bitstream.size:
                raise ValueError("Invalid password or corrupted image")
            msg_bits = bitstream[pos:pos + total_bits].reshape(-1, 8)
            byte_values = msg_bits.dot(weights).astype(np.uint8)
            return bytes(byte_values), filename
        except (ValueError) as e:
            if "Invalid password" in str(e):
                raise
            raise ValueError("Invalid password or corrupted image")

    def steg_write(self, flat_pixels, password, data, filename):
        if not data:
            raise ValueError("Message cannot be empty")

        header = "<{}|{}>".format(len(data), filename)
        num_pixels= flat_pixels.shape[0]
        header_bytes = header.encode("utf-8")
        full_payload = header_bytes + data
        byte_array = np.frombuffer(full_payload, dtype=np.uint8)

        if num_pixels < 44:
            raise ValueError("Image is too small to hide your message.")

        shifts = np.arange(8, dtype=np.uint8)
        message_bits = (byte_array[:, np.newaxis] >> shifts) & 1

        if message_bits.size > (num_pixels - 44) * 3:
            raise ValueError("Message length exceeds image capacity")

        salt = os.urandom(16)
        prp = self.generator.hash_password(password, num_pixels - 44, salt)
        prp_shifted = [i + 44 for i in prp]

        salt_pixels = flat_pixels[:44]
        salt_pixels_shifted = (salt_pixels[
                                   ..., np.newaxis] >> shifts) & 1  # [[255, 230, 211]] -> [[11111111, 0100010101 ,10111010]]
        salt_bytes = np.unpackbits(np.frombuffer(salt, dtype=np.uint8))  # [0,1,1,...1]
        flat_lsb = salt_pixels_shifted[..., 0].flatten()  # Take the least significant bit for every color
        flat_lsb[:128] = salt_bytes  # replace 1st 128 bits with salt bites
        salt_pixels_shifted[..., 0] = flat_lsb.reshape(44, 3)  # Reshape to 3D Matrix
        reconstructed_salt_pixels = np.sum(salt_pixels_shifted << shifts, axis=-1).astype(
            np.uint8)  # Make colors from bits
        flat_pixels[:44] = reconstructed_salt_pixels  # replace original pixels with "salted" pixels

        num_pixels_needed = -(-message_bits.size // 3)
        prp = prp_shifted[:num_pixels_needed]

        chosen_pixels = flat_pixels[prp]
        bits = (chosen_pixels[..., np.newaxis] >> shifts) & 1

        flat_msg = message_bits.flatten()
        bits[..., 0].flat[:len(flat_msg)] = flat_msg

        reconstructed_array = np.sum(bits << shifts, axis=-1).astype(np.uint8)
        flat_pixels[prp] = reconstructed_array

        return flat_pixels

    def steg_write_dct(self, cover_img_path, password, data, filename):
        if not data:
            raise ValueError("Message cannot be empty")

        Y, CbCr, qt = jpeglib.read_dct(cover_img_path) # move to jpeg handler

        num_block_rows = Y.shape[1]
        num_block_cols = Y.shape[2]

        usable_positions = []

        for block_row in range(num_block_rows):
            for block_col in range(num_block_cols):
                for row_in_block in range(8):
                    for col_in_block in range(8):

                        if row_in_block == 0 and col_in_block == 0:
                            continue  #DC ( Direct Current)

                        coefficient = Y[0, block_row, block_col, row_in_block, col_in_block]

                        if abs(coefficient) >= 3:
                            usable_positions.append((block_row, block_col, row_in_block, col_in_block))

        if len(usable_positions) < 128:
            raise ValueError("Image is too small to hide your message.")

        header = "<{}|{}>".format(len(data), filename)
        header_bytes = header.encode("utf-8")
        full_payload = header_bytes + data # bytes

        if len(usable_positions) - 128 < len(full_payload) *8 :
            raise ValueError("Image is too small to hide your message.")

        salt = os.urandom(16)
        prp = self.generator.hash_password(password, len(usable_positions) - 128, salt)
        salt_positions = usable_positions[:128]
        remaining_positions = usable_positions[128:]
        prp_shifted = [i for i in prp]

        salt_bits = [int(bit) for byte in salt for bit in f'{byte:08b}']
        for bit_index, salt_bit in enumerate(salt_bits):
            coordinate = salt_positions[bit_index]
            block_row, block_col, row_in_block, col_in_block = coordinate

            coefficient = Y[0, block_row, block_col, row_in_block, col_in_block]

            if (abs(coefficient) % 2 == 0 and salt_bit == 0) or (abs(coefficient) % 2 == 1 and salt_bit == 1):
                pass
            else:
                if coefficient < 0:
                    Y[0, block_row, block_col, row_in_block, col_in_block] += 1
                else:
                    Y[0, block_row, block_col, row_in_block, col_in_block] -= 1

        payload_bits = [int(bit) for byte in full_payload for bit in f'{byte:08b}']

        for bit_index, salt_bit in enumerate(payload_bits):
            position_index = prp_shifted[bit_index]
            coordinate = remaining_positions[position_index]
            block_row, block_col, row_in_block, col_in_block = coordinate

            coefficient = Y[0, block_row, block_col, row_in_block, col_in_block]

            if (abs(coefficient) % 2 == 0 and salt_bit == 0) or (abs(coefficient) % 2 == 1 and salt_bit == 1):
                pass
            else:
                if coefficient < 0:
                    Y[0, block_row, block_col, row_in_block, col_in_block] += 1
                else:
                    Y[0, block_row, block_col, row_in_block, col_in_block] -= 1

        return Y

    def steg_read_dct(self, Y, password):
        try:
            num_block_rows = Y.shape[1]
            num_block_cols = Y.shape[2]

            usable_positions = []

            for block_row in range(num_block_rows):
                for block_col in range(num_block_cols):
                    for row_in_block in range(8):
                        for col_in_block in range(8):

                            if row_in_block == 0 and col_in_block == 0:
                                continue  # DC ( Direct Current)

                            coefficient = Y[0, block_row, block_col, row_in_block, col_in_block]

                            if abs(coefficient) >= 3:
                                usable_positions.append((block_row, block_col, row_in_block, col_in_block))

            salt_positions = usable_positions[:128]
            remaining_positions = usable_positions[128:]

            salt_bits = []
            for coordinate in salt_positions: # coordinate = (block_row, block_column, row_in_block, column_in_block)
                coef = abs(Y[0, *coordinate])
                if coef % 2 == 0:
                    salt_bits.append(0)
                else:
                    salt_bits.append(1)

            salt = np.packbits(salt_bits).tobytes()

            prp = self.generator.hash_password(password, len(usable_positions) - 128, salt)
            prp_shifted = [i for i in prp]

            pos = 0

            def read_next_byte():
                nonlocal pos
                if pos + 8 > len(prp_shifted):
                    raise ValueError("Invalid password or corrupted image")

                bits = []
                for i in range(8):
                    position_index = prp_shifted[pos + i]
                    coordinate = remaining_positions[position_index]
                    block_row, block_col, row_in_block, col_in_block = coordinate

                    coefficient = Y[0, block_row, block_col, row_in_block, col_in_block]
                    bits.append(abs(coefficient) % 2)

                pos += 8

                byte_value = 0
                for bit in bits:
                    byte_value = (byte_value << 1) | bit

                return byte_value

            if read_next_byte() != ord('<'):
                raise ValueError("Invalid password or corrupted image")

            length_bytes = bytearray()
            while True:
                b = read_next_byte()
                if b == ord('|'):
                    break
                length_bytes.append(b)
            try:
                file_size_bytes = int(length_bytes.decode('ascii'))
            except ValueError:
                raise ValueError("Invalid password or corrupted image")

            total_bits = file_size_bytes * 8

            filename_bytes = bytearray()
            while True:
                b = read_next_byte()
                if b == ord('>'):
                    break
                filename_bytes.append(b)

            filename = filename_bytes.decode('utf-8', errors='replace')

            if total_bits == 0:
                return b"", filename

            if pos + total_bits > len(prp_shifted):
                raise ValueError("Invalid password or corrupted image")
            payload_bytes = bytearray()
            for _ in range(file_size_bytes):
                payload_bytes.append(read_next_byte())
            return bytes(payload_bytes), filename
        except (ValueError) as e:
            if "Invalid password" in str(e):
                raise
            raise ValueError("Invalid password or corrupted image")