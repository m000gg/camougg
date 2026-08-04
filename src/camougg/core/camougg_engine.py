from .steg.steg_write import StegWriter
from .steg.steg_read import StegReader

class CamouggEngine:

    def __init__(self, log_callback=None):
        self.log_callback = log_callback

    def _log(self, message: str):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def embed(self, image_path: str, secret: str, password: str, output_path: str):
        steg_writer = StegWriter()
        self._log(f"Opening image: {image_path}")
        self._log("Encrypting secret message...")
        try:
            steg_writer.steg_write(image_path, password, secret, output_path)
            self._log("Ready!")
        except ValueError as ex:
            self.notify(str(ex), severity="error", timeout=6)
            return False

        self._log("Ready!")
        return True

    def extract(self, image_path: str, password: str):
        steg_reader = StegReader()
        self._log(f"Opening image: {image_path}")
        self._log("Encrypting secret message...")

        try:
            result = steg_reader.steg_read(image_path, password)
            return result
        except ValueError as ex:
            self.notify(str(ex), severity="error", timeout=6)
            return False