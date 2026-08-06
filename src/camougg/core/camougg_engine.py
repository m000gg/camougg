from .steg.steg_write import StegWriter
from .steg.steg_read import StegReader
from pathlib import Path



class CamouggEngine:

    def __init__(self, log_callback=None, app=None):
        self.app = app
        self.log_callback = log_callback

    def _log(self, message: str):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def notify(self, message: str, severity: str = "warning", timeout: float = 3):
        if self.app:
            self.app.notify(message, severity=severity, timeout=timeout)
        else:
            print(f"[{severity}] {message}")

    def embed(self, image_path: str, secret: str, password: str, output_path: str):
        steg_writer = StegWriter()
        if output_path == "same":
            output_path = Path(image_path).parent / "camougg-output-secret.png"

        self._log(f"Opening image: {image_path}")
        self._log("Encrypting secret message...")
        try:
            steg_writer.steg_write(image_path, password, secret, output_path)
            self.notify("Successfully Encrypted the message using your password!", severity="information")
            self._log("Ready!")
        except ValueError as ex:
            error_msg = str(ex) if ex else "Invalid password or corrupted image"
            self._log(f"❌ {error_msg}")
            return False

        self._log("Ready!")
        return True

    def extract(self, image_path: str, password: str):
        steg_reader = StegReader()
        self._log(f"Opening image: {image_path}")
        self._log("Decrypting secret message...")

        try:
            result = steg_reader.steg_read(image_path, password)
            if result is not None:
                self._log(f"Secret: {result}")
                self.notify("Successfully Decrypted the message!", severity="information")
            return result
        except ValueError as ex:
            error_msg = str(ex) if ex else "Invalid password or corrupted image"
            self._log(f"{error_msg}")
            return None