from pathlib import Path

SOURCE_DIR = Path("fixed_pbm")  # folder with cleaned P1 PBMs
OUTPUT_DIR = Path("p4_pbm")     # folder for compact P4 PBMs


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


def read_p1(path):
    with open(path, "rb") as f:
        magic = read_token(f)
        if magic != b"P1":
            raise ValueError("{} is not P1".format(path))

        width = int(read_token(f))
        height = int(read_token(f))

        pixels = []
        needed = width * height

        while len(pixels) < needed:
            tok = read_token(f)
            if tok is None:
                break

            for b in tok:
                if b == 48:      # '0'
                    pixels.append(0)
                elif b == 49:    # '1'
                    pixels.append(1)

                if len(pixels) >= needed:
                    break

        if len(pixels) != needed:
            raise ValueError(
                "{} has wrong pixel count: expected {}, got {}".format(
                    path, needed, len(pixels)
                )
            )

        return width, height, pixels


def write_p4(path, width, height, pixels):
    row_bytes = (width + 7) // 8

    with open(path, "wb") as f:
        f.write(b"P4\n")
        f.write("{} {}\n".format(width, height).encode("ascii"))

        for y in range(height):
            row = pixels[y * width:(y + 1) * width]
            out = bytearray(row_bytes)

            for x, p in enumerate(row):
                if p:
                    out[x // 8] |= 1 << (7 - (x % 8))

            f.write(out)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    files = sorted(SOURCE_DIR.glob("*.pbm"))
    if not files:
        print("No P1 files found in", SOURCE_DIR.resolve())
        return

    total_before = 0
    total_after = 0

    for path in files:
        width, height, pixels = read_p1(path)
        out_path = OUTPUT_DIR / path.name
        write_p4(out_path, width, height, pixels)

        before = path.stat().st_size
        after = out_path.stat().st_size
        total_before += before
        total_after += after

        print("{}: {} bytes -> {} bytes".format(path.name, before, after))

    print()
    print("Done")
    print("Output folder:", OUTPUT_DIR.resolve())
    print("Total before:", total_before, "bytes")
    print("Total after :", total_after, "bytes")


if __name__ == "__main__":
    main()