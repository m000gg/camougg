import os

class PayloadIO:

    def write_payload(self, data: bytes, filename: str, output_dir: str) -> str:
        safe_filename = os.path.basename(filename)
        if not safe_filename or safe_filename != filename or safe_filename in {".", ".."}:
            raise ValueError("Invalid password or corrupted image")
        output_path = os.path.join(output_dir, safe_filename)
        with open(output_path, "wb") as f:
            f.write(data)
        return output_path

    def read_payload(self, path) -> tuple[bytes, str]:
        try:
            with open(path, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Payload file not found: {path}")
        filename = os.path.basename(path)
        return data, filename