import os
import time
from Pico_ePaper_3_7 import EPD_3in7

SECONDS_PER_CARD = 60


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


def list_pbm_files():
    files = []

    for name in os.listdir():
        if (
            name.lower().endswith(".pbm")
            and len(name) >= 7
            and name[0:2].isdigit()
            and name[2] == "_"
        ):
            files.append(name)

    files.sort()
    return files


def draw_pixel(epd, x, y, black):
    epd.image1Gray.pixel(x, y, 0 if black else 1)


def put_pixel(epd, x, y, black, rotated):
    if rotated:
        tx = y
        ty = epd.height - 1 - x
        draw_pixel(epd, tx, ty, black)
    else:
        draw_pixel(epd, x, y, black)


def load_p4_into_buffer(filename, epd):
    with open(filename, "rb") as f:
        magic = read_token(f)
        if magic != b"P4":
            raise ValueError("PBM file must be P4: " + filename)

        pbm_w = int(read_token(f))
        pbm_h = int(read_token(f))

        epd_w = epd.width
        epd_h = epd.height

        same = (pbm_w == epd_w and pbm_h == epd_h)
        rotated = (pbm_w == epd_h and pbm_h == epd_w)

        if not same and not rotated:
            raise ValueError(
                "PBM size must be {}x{} or {}x{}: {}".format(
                    epd_w, epd_h, epd_h, epd_w, filename
                )
            )

        epd.image1Gray.fill(0xFF)

        row_bytes = (pbm_w + 7) // 8

        for y in range(pbm_h):
            row = f.read(row_bytes)
            if len(row) != row_bytes:
                raise ValueError("Unexpected end of P4 raster data: " + filename)

            x = 0
            for byte in row:
                for bit in range(7, -1, -1):
                    if x >= pbm_w:
                        break
                    black = ((byte >> bit) & 1) == 1
                    put_pixel(epd, x, y, black, rotated)
                    x += 1


def show_card(epd, filename):
    try:
        print("Opening:", filename)
        load_p4_into_buffer(filename, epd)
        print("Calling display...")
        epd.EPD_3IN7_1Gray_Display(epd.buffer_1Gray)
        return True
    except Exception as e:
        print("Skipping {}: {}".format(filename, e))
        return False


def main():
    epd = EPD_3in7()
    epd.EPD_3IN7_1Gray_init()

    pbm_files = list_pbm_files()
    print("PBM files:", pbm_files)

    if not pbm_files:
        print("No numbered alphabet PBM files found.")
        time.sleep(2)
        epd.Sleep()
        return

    try:
        while True:
            for filename in pbm_files:
                shown = show_card(epd, filename)
                if shown:
                    time.sleep(SECONDS_PER_CARD)
                else:
                    time.sleep(1)
    finally:
        epd.Sleep()


main()