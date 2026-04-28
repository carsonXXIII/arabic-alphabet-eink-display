import os
from pathlib import Path

SOURCE_DIR = Path(".")
OUTPUT_DIR = Path("fixed_pbm")


def read_token(f):
    token = bytearray()

    while True:
        ch = f.read(1)

        if not ch:
            if token:
                return bytes(token)
            return None

        if ch == b"#":
            while True:
                ch = f.read(1)
                if not ch or ch in b"\r\n":
                    break
            if token:
                return bytes(token)
            continue

        if ch in b" \t\r\n":
            if token:
                return bytes(token)
            continue

        token.extend(ch)


def read_header_and_data_offset(f):
    magic = read_token(f)
    if magic is None:
        raise ValueError("Empty file")

    magic = magic.decode("ascii", errors="strict")
    if magic not in ("P1", "P4"):
        raise ValueError("Unsupported PBM magic: {}".format(magic))

    wtok = read_token(f)
    htok = read_token(f)

    if wtok is None or htok is None:
        raise ValueError("Missing width/height")

    width = int(wtok)
    height = int(htok)

    if width <= 0 or height <= 0:
        raise ValueError("Invalid dimensions {}x{}".format(width, height))

    offset = f.tell()
    return magic, width, height, offset


def parse_p1_lenient(raw, width, height):
    needed = width * height
    pixels = []

    i = 0
    n = len(raw)

    while i < n and len(pixels) < needed:
        b = raw[i]

        if b == 35:
            i += 1
            while i < n and raw[i] not in (10, 13):
                i += 1
            continue

        if b in (9, 10, 13, 32):
            i += 1
            continue

        if b == 48 or b == 49:
            pixels.append(1 if b == 49 else 0)
            i += 1
            continue

        token = bytearray()
        while i < n and raw[i] not in (9, 10, 13, 32, 35):
            token.append(raw[i])
            i += 1

        found = False
        for c in token:
            if c == 48 or c == 49:
                pixels.append(1 if c == 49 else 0)
                found = True
                if len(pixels) >= needed:
                    break

        if not found:
            raise ValueError("Invalid non-bitmap token: {!r}".format(bytes(token[:40])))

    if len(pixels) != needed:
        raise ValueError(
            "Not enough P1 pixels: expected {}, got {}".format(needed, len(pixels))
        )

    return pixels


def parse_p4(raw, width, height):
    row_bytes = (width + 7) // 8
    expected = row_bytes * height

    if len(raw) < expected:
        raise ValueError(
            "Not enough P4 bytes: expected {}, got {}".format(expected, len(raw))
        )

    pixels = []
    idx = 0

    for _y in range(height):
        row = raw[idx:idx + row_bytes]
        idx += row_bytes

        x = 0
        for byte in row:
            for bit in range(7, -1, -1):
                if x >= width:
                    break
                pixels.append(1 if ((byte >> bit) & 1) else 0)
                x += 1

    return pixels


def write_p1(path, width, height, pixels):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="\n") as f:
        f.write("P1\n")
        f.write("{} {}\n".format(width, height))

        for y in range(height):
            row = pixels[y * width:(y + 1) * width]
            f.write(" ".join("1" if p else "0" for p in row))
            f.write("\n")


def validate_or_fix_pbm(path):
    size = path.stat().st_size

    if size == 0:
        return {
            "file": str(path),
            "status": "EMPTY",
            "width": None,
            "height": None,
            "note": "0-byte file; cannot recover",
            "pixels": None,
        }

    with open(path, "rb") as f:
        magic, width, height, offset = read_header_and_data_offset(f)
        f.seek(offset)
        body = f.read()

    if magic == "P4":
        pixels = parse_p4(body, width, height)
        return {
            "file": str(path),
            "status": "OK",
            "width": width,
            "height": height,
            "note": "valid P4",
            "pixels": pixels,
        }

    try:
        pixels = parse_p1_lenient(body, width, height)
        return {
            "file": str(path),
            "status": "OK",
            "width": width,
            "height": height,
            "note": "valid/fixed P1",
            "pixels": pixels,
        }
    except Exception as p1_error:
        try:
            pixels = parse_p4(body, width, height)
            return {
                "file": str(path),
                "status": "RECOVERED",
                "width": width,
                "height": height,
                "note": "header said P1 but body matched P4 ({})".format(p1_error),
                "pixels": pixels,
            }
        except Exception as p4_error:
            return {
                "file": str(path),
                "status": "BROKEN",
                "width": width,
                "height": height,
                "note": "P1 failed: {}; P4 failed: {}".format(p1_error, p4_error),
                "pixels": None,
            }


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    pbm_files = sorted(
        p for p in SOURCE_DIR.rglob("*.pbm")
        if OUTPUT_DIR not in p.parents
    )

    if not pbm_files:
        print("No .pbm files found under", SOURCE_DIR.resolve())
        return

    print("Found {} PBM files".format(len(pbm_files)))
    print()

    repaired = 0
    broken = 0
    empty = 0

    for path in pbm_files:
        try:
            result = validate_or_fix_pbm(path)
        except Exception as e:
            print("[BROKEN] {} -> {}".format(path, e))
            broken += 1
            continue

        status = result["status"]
        width = result["width"]
        height = result["height"]
        note = result["note"]

        if status in ("OK", "RECOVERED"):
            out_path = OUTPUT_DIR / path.name
            write_p1(out_path, width, height, result["pixels"])
            print("[{}] {} -> {}x{} -> {}".format(status, path, width, height, note))
            repaired += 1
        elif status == "EMPTY":
            print("[EMPTY] {} -> {}".format(path, note))
            empty += 1
        else:
            print("[BROKEN] {} -> {}".format(path, note))
            broken += 1

    print()
    print("Finished")
    print("Fixed files written to:", OUTPUT_DIR.resolve())
    print("Usable files:", repaired)
    print("Broken files:", broken)
    print("Empty files:", empty)


if __name__ == "__main__":
    main()