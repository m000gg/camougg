# Feature #2: Least Significant Bit (LSB) Embedding

---
## Changelog

| Version  | Date       | Description                                                                                                                                             | Authors                             |
|----------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------|
| 1.0      | 2026-08-03 | Initial Description                                                                                                                                     | [m000gg](https://github.com/m000gg) |
| 1.1      | 2026-08-04 | Fixed header example, clarified header decoding vs vectorized message decoding                                                                          | [m000gg](https://github.com/m000gg) |
| 2.0      | 2026-08-14 | MVP2: random per-embed salt with a fixed unpermuted salt zone, arbitrary-file (bytes) payload instead of UTF-8-only text, extended header with filename | [m000gg](https://github.com/m000gg) |

---

- Issue #6 ➔ PR #8

# 👔 Part 1: Product & Business

## Executive Summary

`LSBEncoder` provides the core steganographic mechanism used by CamouGG for hiding
arbitrary files inside an image.

Instead of modifying the visual appearance of the image, the algorithm changes only
the **Least Significant Bit (LSB)** of selected RGB color channels. Since modifying
the least significant bit changes the color value by at most one intensity level,
the alteration is practically invisible to the human eye while still allowing
deterministic recovery of the embedded payload.

As of MVP2, the container is split into two zones: a small **fixed, unpermuted salt
zone** at the start of the image, and a **permuted payload zone** covering the rest.
The salt zone stores a randomly generated, per-embed salt in plain raster order —
this is the only piece of data whose location does not depend on the password. The
salt is what makes the pixel permutation (see Feature #1) different on every embed,
even when the same password is reused on the same container.

The actual order of modified pixels in the payload zone is **not** decided by this
feature. Instead, pixel traversal order is provided externally by the
password-and-salt-based cryptographic permutation generator (see Feature #1).

## Feature objectives

- Embed an arbitrary binary file (not just UTF-8 text) into RGB images, byte-for-byte.
- Generate a new random salt on every embed and store it in a fixed, unpermuted zone
  so two embeds with the same password never produce identical output.
- Preserve visual quality by modifying only one bit per color channel.
- Recover the original file, and its original filename, without any information loss.
- Work deterministically together with the password-and-salt-based pixel permutation.

## Feature scope

### In scope

- Converting an arbitrary file's bytes into a bit stream.
- Generating a random salt per embed and writing it to a fixed, unpermuted zone.
- Embedding bits into the least significant bits of RGB values.
- Restoring bytes from extracted LSBs.
- Reading and writing message headers, including payload length and filename.
- Capacity validation (salt zone + header + payload against container size).

### Out of scope

- Selecting embedding locations within the payload zone (handled by Feature #1).
- Image loading/saving.
- Password-to-key derivation (handled by Feature #1).
- Encryption of the payload content itself (separate crypto module).
- JPEG/DCT-domain embedding (separate feature).

## User flow

```mermaid
flowchart TD

A["Input file bytes"] --> B["Header Generation: <payload_length|filename>"]
B --> C["Concatenate header + payload bytes"]
C --> D["Convert bytes to bit stream"]

R["Generate random salt (os.urandom)"] --> S["Write salt to fixed unpermuted zone (first 44 pixels)"]
S --> E["Derive pixel permutation from password + salt"]

D --> F["Replace LSB of selected RGB channels (permuted zone)"]
E --> F
F --> G["Save modified image"]


H["Stego image"] --> I["Read salt from fixed unpermuted zone (first 44 pixels)"]
I --> J["Derive identical pixel permutation from password + salt"]
J --> K["Read LSB stream from permuted zone"]
K --> L["Decode header: payload_length + filename"]
L --> M["Recover payload bits"]
M --> N["Recovered file bytes + filename"]
```

## Use cases

### 1. Embedding

The user supplies a file (bytes) and a password.

A fresh random salt is generated and written to the fixed salt zone, in plain
raster order, without any password-derived permutation.

The password and salt together determine the pixel order for the rest of the
container (Feature #1).

The LSB encoder embeds every header bit and every payload bit into the least
significant bit of one RGB channel, within the permuted zone.

### 2. Successful extraction

The salt is read directly from the fixed zone — no password is needed for this step.

The same password, combined with that salt, generates the identical pixel
permutation for the payload zone.

The encoder reads the same LSB sequence, reconstructs the original header and
payload bytes, and returns the original filename and file content.

### 3. Wrong password

The salt zone is read correctly regardless of the password (it isn't permuted).

A wrong password produces a different derived permutation for the payload zone, so
LSBs are read in the wrong order.

The reconstructed byte stream becomes random noise, preventing successful header
parsing or payload recovery. This surfaces as a generic error when the header
terminator cannot be located/parsed, or when the declared payload length exceeds
what is available — no partial file is returned.

### 4. Same password, same container, repeated embed

Because a new random salt is generated on every embed, the derived key and pixel
permutation differ between embeds even when the password and source image are
identical. Two embeds of the same file with the same password therefore produce
different stego images.

### 5. Capacity overflow

If the container is smaller than the fixed salt zone, embedding is rejected
immediately.

If the header (payload length + filename) plus the payload requires more bits than
available in the remaining (permuted) zone, embedding is aborted before modifying
the image.

The same validation is performed on the read path: if the declared payload length
in the header exceeds the remaining available bits, extraction is aborted with an
error instead of returning corrupted data.

## Functional Requirements

- Accept an arbitrary binary payload (`bytes`), not only UTF-8 text.
- Generate a new random salt (`os.urandom(16)`) on every embed call.
- Write the salt to a fixed, unpermuted zone at the start of the container, in
  plain raster order.
- Read the salt back automatically on extract, without any manual input.
- Derive the pixel permutation for the payload zone from `password + salt`,
  restricted to the pixel range outside the salt zone.
- Convert the header and payload into a bit stream.
- Embed one payload bit into one RGB channel, within the payload zone only.
- Support arbitrary image dimensions above the minimum required by the salt zone.
- Recover the original payload bytes and filename exactly.
- Detect payloads exceeding available capacity, both during embedding and
  extraction, before any partial data is written or returned.
- Preserve all bits except the least significant one.

## Non-Functional Requirements

- Image distortion must remain visually imperceptible.
- Memory usage should scale linearly with payload size.
- The implementation must operate deterministically given the same password, salt,
  and container.
- Time complexity: message body decoding is a single vectorized NumPy operation
  (O(n) over bits, no Python-level loop). Header decoding is performed byte-by-byte
  in a Python loop, since the header's own length is not known in advance; this
  loop is bounded by the number of pixels in the payload zone in the worst case
  (e.g. wrong password with no `>` terminator found).
- Salt-zone encoding/decoding is a fixed-cost operation independent of payload
  size (constant 44-pixel zone).

# 🛠 Part 2: Technical Realisation

## Architecture & Integrations

**Tools used**

- Pillow — image loading/saving.
- NumPy — vectorized manipulation of RGB arrays.
- `os.urandom` — cryptographically secure salt generation.
- UTF-8 encoding/decoding (header only — see Design Decision 5).
- Password-and-salt-based permutation generator (Feature #1).

## Explanation of the design decisions

### 1. Image conversion to RGB

```python
img.convert("RGB")
```

The embedding algorithm always operates on RGB images regardless of the original
image mode. This guarantees that every pixel consists of exactly three independent
8-bit color channels.

---

### 2. Image represented as a NumPy array, flattened

```python
pixel_array = np.array(img_rgb)
flat_pixels = pixel_array.reshape(-1, 3)
```

The image becomes `number_of_pixels × RGB` instead of individual Pillow pixel
objects, giving every pixel a single integer index.

---

### 3. Fixed salt zone (first 44 pixels)

```python
salt_pixels = flat_pixels[:44]
```

A new 16-byte salt (`os.urandom(16)`) is generated on every embed. At 3 usable LSB
slots per pixel (one per RGB channel), 128 bits of salt require 44 pixels
(`ceil(128 / 3) = 43`, rounded up to a whole-pixel boundary to keep the zone simple
and avoid partially-used pixels). The last 4 of the 132 available slots in this
zone are unused.

This zone is **not** permuted — it is written and read in plain raster order
(`flat_pixels[:44]`), independent of the password. This is a deliberate design
choice, not an oversight: the permutation for the rest of the container is derived
*from* the salt, so the salt cannot itself live inside the permuted space without
creating a circular dependency (you would need the salt to find the salt).

Only the LSB (bit-plane 0) of each channel in this zone is modified — the same
"decompose into 8 bit-planes, replace plane 0, recompose" approach used for the
payload zone (see Decision 6).

---

### 4. Deriving the payload-zone permutation from password + salt

```python
prp = generator.hash_password(password, num_pixels - 44, salt)
prp_shifted = [i + 44 for i in prp]
```

The permutation generator (Feature #1) is called with a restricted pixel count
(`num_pixels - 44`), so it can never produce an index that falls inside the salt
zone. The returned indices (range `[0, num_pixels - 45]`) are then shifted by `+44`
to map them onto the actual payload-zone pixel range (`[44, num_pixels - 1]`).
Because the domain is restricted *before* generation (not filtered *after*), a
collision with the salt zone is structurally impossible, not merely unlikely.

On read, the same salt (recovered from the fixed zone) and the same password
reproduce the identical `prp_shifted`, so header and payload are read from exactly
the pixels they were written to.

---

### 5. Header generation

Before embedding, the payload receives a textual header:

```
<payload_length|filename>
```

Example:

```
<45231|report_final.pdf>10110011...
```

- `payload_length` — the number of payload bytes that follow, so extraction knows
  exactly how many bits to read.
- `filename` — the original file's full name including extension, so the original
  file name is preserved on extraction rather than replaced with a generic output
  name.

The header itself is composed only of ASCII digits, `<`, `>`, `|`, and filename
characters — it is always valid UTF-8, so it can safely continue to be decoded as
text. This is unrelated to, and unaffected by, the payload no longer being
UTF-8-safe (see Decision 6).

---

### 6. Header stays text; payload becomes raw bytes

The header is still encoded as UTF-8 text (see Decision 5) — that part of the
design does not change from v1.

The payload, however, is treated as raw `bytes` end-to-end and is **never**
passed through `.decode("utf-8", errors="replace")`. In v1, decoding the message
body as UTF-8 was safe because the body was always text. For arbitrary files, the
byte stream is not guaranteed to be valid UTF-8 at all — decoding it with
`errors="replace"` would silently substitute a placeholder character for any byte
sequence that isn't valid UTF-8, corrupting the payload irrecoverably and breaking
byte-for-byte round-trip. The payload is therefore returned as `bytes` directly
from the reconstructed channel values, with no text decoding step.

---

### 7. Byte-to-bit conversion

Each byte (from the header and from the payload) is decomposed into eight
individual bits, e.g. `01000001` becomes `0 1 0 0 0 0 0 1`. These bits form the
stream embedded into the payload zone of the image.

---

### 8. Least Significant Bit replacement

For every selected RGB channel in the payload zone, only the least significant bit
is replaced — e.g. `10101100` embedding a `1` becomes `10101101`. Every channel
therefore changes by at most `±1`, which is visually imperceptible. This is
identical to how the salt zone is written (Decision 3), just applied to a
different pixel range with a different index source (`prp_shifted` instead of
plain raster order).

---

### 9. Capacity validation

Before modifying the image, the encoder verifies, in this order:

1. `num_pixels >= 44` — the container is large enough to even hold the salt zone.
2. `(header_bits + payload_bits) <= (num_pixels - 44) * 3` — the header plus
   payload fit within the remaining payload-zone capacity.

Both checks happen **before** the (comparatively expensive) permutation is
generated, so an oversized payload is rejected immediately rather than after
paying the cost of `hash_password`. This prevents incomplete writes and corrupted
payloads.

The same validation is performed on the read path, both while searching for the
header terminator and after the header is decoded, to prevent reading past the end
of the available bitstream.

---

### 10. Reconstruction

After modifying the selected channels in both the salt zone and the payload zone,
the modified pixel array is reshaped back into its original `height × width × RGB`
dimensions and written as a new image.

---

### 11. Extraction

Extraction performs the reverse process:

1. Read the salt from the fixed zone (`flat_pixels[:44]`), no password required
   for this step.
2. Derive the identical payload-zone permutation from `password + salt`.
3. Read the LSB of every selected channel in the payload zone sequentially and
   flatten into a single bitstream.
4. Decode the header one byte at a time until the `>` terminator is found, since
   the header's own length is not known ahead of time; split on `|` to recover
   `payload_length` and `filename` separately.
5. Once the header is parsed, the payload length becomes known, and the remaining
   payload bits are decoded in a single vectorized step: the bitstream is reshaped
   into `(payload_length, 8)` and converted to byte values via a dot product with
   bit weights `[1, 2, 4, 8, 16, 32, 64, 128]`.
6. Return the raw payload `bytes` (no UTF-8 decoding — see Decision 6) together
   with the recovered `filename`.

```mermaid
graph TD

A[File bytes] --> B["Header Creation: <len|filename>"]
B --> C[Convert header+payload to bits]

S1[os.urandom salt] --> S2[Write salt to fixed zone]
S2 --> D[Derive permutation from password+salt]

C --> E["Replace LSB of selected RGB channels"]
D --> E
E --> F[Modified image]

F --> G["Read salt from fixed zone"]
G --> H[Derive identical permutation]
H --> I[Read LSBs from payload zone]
I --> J[Restore header + payload bytes]
J --> K[Recovered file bytes + filename]
```

## Data models

This feature does not create any persistent data or database models.

Input:

- `data: bytes` — the file content to embed.
- `filename: str` — the original file's full name, including extension.
- `password: str`
- RGB image.

Output (embed):

- Modified RGB image after embedding (salt zone + payload zone).

Output (extract):

- `filename: str` — the recovered original file name.
- `data: bytes` — the recovered original file content, byte-for-byte.

## Open questions

### Q1 (resolved in v2.0)

> The current implementation stores the payload length as a textual header
> (`<123>`). Would a fixed-size binary header reduce overhead while simplifying
> parsing?

Kept textual for MVP2 (`<payload_length|filename>`) — the header is small relative
to typical payloads, and text parsing is already implemented and tested. A
fixed-size binary header remains an option for a future revision if header
overhead becomes a measured concern.

### Q2

The current implementation modifies one bit per RGB channel. Should future
versions optionally support using multiple least significant bits (2-LSB, 3-LSB)
to increase embedding capacity while accepting greater visual distortion?

*(Out of scope for MVP2 — explicitly deferred.)*

### Q3

The write path currently instantiates its own generator locally
(`generator = CSPRNGenerator()`), while the read path accesses it via
`self.generator`. Should generator ownership be unified — e.g. always injected via
`__init__` — to keep write and read symmetric within the same class?

### Q4 (new in v2.0)

The salt zone is fixed at 44 pixels regardless of container size. For very small
containers, this represents a proportionally larger fixed cost. Should the minimum
supported container size be explicitly documented/enforced elsewhere (e.g. in the
TUI or a top-level `embed()` wrapper), rather than only surfacing as a capacity
error at write time?