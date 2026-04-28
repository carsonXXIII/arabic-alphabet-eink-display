<!--
  Arabic Alphabet E-Ink Display
  Author: Carson's Projects
-->

# Arabic Alphabet E‑Ink Display

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Raspberry Pi Pico](https://img.shields.io/badge/Platform-Raspberry%20Pi%20Pico-raspberry.svg)]()
[![Display: 3.7-inch E‑Paper](https://img.shields.io/badge/Display-3.7%E2%80%B3%20E--Ink-lightgrey.svg)]()

A Raspberry Pi Pico and e‑paper project that cycles through the 28 letters of the Arabic alphabet on a 3.7‑inch e‑ink display. Each screen shows a single Arabic letter with its transliteration, creating a low‑power, distraction‑free study tool for learning the Arabic script. 
---

## ✨ Features

- 28 slides for the full Arabic alphabet (ا … ي) 
- One letter per screen for maximum readability
- Transliteration shown under each letter
- Runs on Raspberry Pi Pico with a 3.7‑inch e‑paper panel 
- Automatically cycles through letters at a configurable interval
- Designed to autostart when saved as `main.py` on the Pico 

---

## 🧱 Hardware

- **Microcontroller:** Raspberry Pi Pico
- **Display:** 3.7‑inch e‑paper / e‑ink display (Waveshare‑style, 480×280)
- **Power:** Micro USB cable or other 5V source
- **Wiring:** Standard SPI connection between Pico and e‑paper driver board

You’ll need to follow the wiring pinout recommended by your e‑paper module or the `Pico_ePaper_3_7` driver library. 

---

## 🧰 Software & Dependencies

- **Firmware:** MicroPython for Raspberry Pi Pico 
- **Display driver:** `Pico_ePaper_3_7` (or equivalent 3.7″ e‑paper driver module) 
- **Assets:** A set of PBM bitmap files, one for each Arabic letter slide

The Pico reads the PBM files directly from its filesystem and streams them into the display buffer.

---

## 📁 Project Structure

Typical repository layout:

```text
/
├─ main.py               # MicroPython slideshow script (runs on the Pico)
├─ 01_alif.pbm
├─ 02_baa.pbm
├─ 03_taa.pbm
├─ ...
├─ 28_yaa.pbm
└─ tools/
   ├─ fix_pbm_files.py   # Optional: desktop helper to validate/clean PBMs
   └─ convert_to_p4.py   # Optional: desktop helper to compress PBMs
```

On the Pico itself, all `.pbm` files should live in the same directory as `main.py` (usually the root of the device).
---

## 🧠 How it works

Instead of rendering Arabic text directly on the microcontroller, this project uses **pre‑rendered bitmap slides**. Each PBM file encodes one flashcard:

- Large Arabic letter (in the appropriate joined form, if you choose to do that)
- Transliteration beneath it
- Clean spacing so the glyph and text never overlap [cite:193][cite:194]

At runtime:

1. `main.py` discovers the PBM files (e.g., `01_alif.pbm` … `28_yaa.pbm`).
2. The script loads each PBM, pushing the bits into the e‑paper framebuffer.
3. The display is refreshed.
4. The code waits `SECONDS_PER_CARD` seconds.
5. The slideshow advances to the next letter and repeats. 

This bitmap‑first design produces consistent typography and layout on constrained hardware. 

---

## 🚀 Getting Started

### 1. Flash MicroPython onto the Pico

Follow the official Raspberry Pi Pico MicroPython guide to flash the UF2 firmware. 

### 2. Wire the display

Connect the Pico to your 3.7″ e‑paper module according to the driver documentation (SPI pins, DC, CS, RST, BUSY, VCC, GND).

### 3. Upload code and assets

Using Thonny or another MicroPython IDE:

1. Upload `main.py` to the Pico.
2. Upload all `NN_name.pbm` bitmap files to the **same directory** as `main.py`.
3. (Optional) Remove any old or unused PBM files to free flash space.

### 4. Autostart on power‑up

If your script is named `main.py` and stored on the Pico filesystem, MicroPython will execute it automatically each time the board powers up or resets. 

---

## ⚙️ Configuration

Inside `main.py` you’ll find:

```python
SECONDS_PER_CARD = 60
```

Change this value to adjust how long each slide stays on screen:

- `SECONDS_PER_CARD = 10`  → 10 seconds per letter
- `SECONDS_PER_CARD = 300` → 5 minutes per letter

If you add more letters, cards, or lesson modes, you can extend the file naming convention and the loop that cycles through files.

---

## 📚 Learning focus

The project is tuned for self‑study:

- One clear letter at a time 
- A consistent transliteration style beneath each letter 
- No extra UI or animations to distract from the glyph

It’s a physical, always‑ready flashcard device — ideal for a desk or bedside table while you memorize the script. 

---

## 🛠️ Development notes

The PBM assets were generated and cleaned on a PC first, then uploaded to the Pico:

- Plain PBM (`P1`) or compact PBM (`P4`) formats can be used, as long as the loader matches.
- Desktop helper scripts can validate the PBM headers, ensure the correct width/height, and re‑encode malformed files before deployment.
- Because Pico flash is limited, using compact formats (like `P4`) is recommended if you add more slides or higher‑resolution assets. 

---

## 🧭 Roadmap / Ideas

- Example words for each letter (with position‑specific forms)
- Initial / medial / final form variants per letter
- Button inputs to move forwards/backwards manually
- Simple quiz modes (e.g., hide transliteration until a button is pressed)
- Battery‑powered enclosure with a power switch

---

## 📝 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details. 

---

## 🙋‍♂️ Author
Carson's Projects
Built as a personal learning project to explore MicroPython, e‑paper displays, and the Arabic alphabet.
