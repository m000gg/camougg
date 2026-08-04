from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import hashlib

class CSPRNGenerator:
    def __init__(self):
        self.static_salt = b"camougg"
        self.nonce = b'1234567890123456'

    def hash_password(self, password, num_pixels):
        pixel_indices = [i for i in range(num_pixels)]
        password = password.encode("utf-8")

        key = hashlib.scrypt(password, salt=self.static_salt, n=16384, r=8, p=1, dklen=32)

        cipher = Cipher(algorithms.ChaCha20(key, self.nonce), mode=None)
        encryptor = cipher.encryptor()

        raw_bytes = encryptor.update(bytes(num_pixels * 4))

        random_stream = []
        for i in range(0, len(raw_bytes), 4):

            chunk = raw_bytes[i: i + 4]

            big_number = int.from_bytes(chunk, byteorder='little')
            random_stream.append(big_number)

        for i in range(0, len(pixel_indices)-1):
            free_places = len(random_stream) - i
            q = random_stream[i] % free_places
            pixel_indices[len(pixel_indices)-1-i], pixel_indices[q] = pixel_indices[q], pixel_indices[len(pixel_indices)-1-i]


        return pixel_indices
