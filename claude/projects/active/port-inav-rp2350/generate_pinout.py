#!/usr/bin/env python3
"""
Generate INAV Option C pinout diagram for Raspberry Pi Pico 2 (RP2350).
Annotates the back-of-board photo with INAV function labels for each pin.
Each label box is single-line with comfortable vertical padding.
"""

from PIL import Image, ImageDraw, ImageFont
import os

BASE = '/home/raymorris/Documents/planes/inavflight'
IMG_PATH = f'{BASE}/claude/projects/active/port-inav-rp2350/Raspberry-Pi-Pico-2-back.webp'
OUT_PATH = f'{BASE}/claude/projects/active/port-inav-rp2350/rp2350-pico2-inav-pinout.png'

# ── Colour scheme ─────────────────────────────────────────────────────────────
FG = {
    'uart':  '#1144CC',
    'spi':   '#6600AA',
    'motor': '#CC1111',
    'servo': '#BB5500',
    'i2c':   '#006622',
    'adc':   '#886600',
    'led':   '#006688',
    'power': '#333333',
    'other': '#554466',
}
BG = {
    'uart':  '#D8E8FF',
    'spi':   '#EDD8FF',
    'motor': '#FFD8D8',
    'servo': '#FFE8CC',
    'i2c':   '#D8FFE8',
    'adc':   '#FFF8CC',
    'led':   '#CCF8FF',
    'power': '#E8E8E8',
    'other': '#EED8EE',
}

# ── Option C pin definitions ──────────────────────────────────────────────────
# LEFT side of back-of-board image = pins 40→21 top-to-bottom (VBUS → GP16)
LEFT_PINS = [
    # (display label,          group)
    ('VBUS (5V)',              'power'),
    ('VSYS',                  'power'),
    ('GND',                   'power'),
    ('3V3_EN',                'power'),
    ('3.3V',                  'power'),
    ('ADC_VREF',              'power'),
    ('RSSI / BEEPER',         'adc'),    # GP28 ADC2 dual-use
    ('GND (analog)',          'power'),  # AGND
    ('CURRENT',               'adc'),    # GP27 ADC1
    ('VBAT',                  'adc'),    # GP26 ADC0
    ('RUN',                   'other'),
    ('LED Strip (WS2812)',    'led'),    # GP22 PIO2 SM0
    ('GND',                   'power'),
    ('SERVO 2',               'servo'),  # GP21 PWM slice 10B
    ('SERVO 1',               'servo'),  # GP20 PWM slice 10A
    ('I2C SCL',               'i2c'),    # GP19 I2C1
    ('I2C SDA',               'i2c'),    # GP18 I2C1
    ('GND',                   'power'),
    ('BEEPER',                'other'),  # GP17
    ('SPI CS (Flash)',        'spi'),    # GP16 SPI0 CS blackbox flash
]

# RIGHT side of back-of-board image = pins 1→20 top-to-bottom (GP0 → GP15)
RIGHT_PINS = [
    ('UART1 TX',              'uart'),   # GP0  UART0 TX – MSP/configurator
    ('UART1 RX',              'uart'),   # GP1  UART0 RX
    ('GND',                   'power'),
    ('UART2 TX',              'uart'),   # GP2  UART1 TX – CRSF/SBUS
    ('UART2 RX',              'uart'),   # GP3  UART1 RX
    ('SPI MISO',              'spi'),    # GP4  SPI0 RX – gyro + flash bus
    ('SPI CS (Gyro)',         'spi'),    # GP5  SPI0 CSn
    ('GND',                   'power'),
    ('SPI SCK',               'spi'),    # GP6  SPI0 SCK
    ('SPI MOSI',              'spi'),    # GP7  SPI0 TX
    ('UART3 TX / SERVO 3',   'servo'),  # GP8  PIO1 SM0 / PWM4A dual-use
    ('UART3 RX / SERVO 4',   'servo'),  # GP9  PIO1 SM1 / PWM4B dual-use
    ('GND',                   'power'),
    ('M1',                    'motor'),  # GP10 PIO0 SM0 DShot  ← BF MOTOR1
    ('M2',                    'motor'),  # GP11 PIO0 SM1 DShot  ← BF MOTOR2
    ('M3',                    'motor'),  # GP12 PIO0 SM2 DShot  ← BF MOTOR3
    ('M4',                    'motor'),  # GP13 PIO0 SM3 DShot  ← BF MOTOR4
    ('GND',                   'power'),
    ('UART4 TX / SERVO 5',   'servo'),  # GP14 PIO1 SM2 / PWM7A dual-use
    ('UART4 RX / SERVO 6',   'servo'),  # GP15 PIO1 SM3 / PWM7B dual-use
]

# ── Board geometry calibration (original 667×667 image coordinates) ───────────
X_LEFT_PAD  = 97    # x of left-column pad centres
X_RIGHT_PAD = 570   # x of right-column pad centres
Y_FIRST     = 63    # y of first pin (top)
Y_LAST      = 623   # y of last pin (bottom)
N_PINS      = 20

EXTEND  = 290       # extra canvas pixels added to each horizontal side
TITLE_H = 50        # extra pixels added above image for title

# ── Helpers ───────────────────────────────────────────────────────────────────
FONT_PATHS = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
]

def load_font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def text_size(font, text):
    bb = font.getbbox(text)
    return bb[2] - bb[0], bb[3] - bb[1]

# ── Single-line label drawers ─────────────────────────────────────────────────
VPAD = 7   # vertical padding inside each label box
HPAD = 6   # horizontal padding inside each label box

def draw_left_label(draw, x_pad, y, label, fg, bg, font):
    """Single-line label to the LEFT of the pad (right-aligned)."""
    tw, th = text_size(font, label)
    line_end  = x_pad - 6
    box_right = line_end - 8
    box_left  = box_right - tw - HPAD * 2

    draw.rectangle([box_left, y - th // 2 - VPAD,
                    box_right + 1, y + th // 2 + VPAD],
                   fill=bg, outline=fg, width=1)
    draw.text((box_right - tw - HPAD, y - th // 2), label, fill=fg, font=font)
    draw.line([(box_right + 2, y), (line_end, y)], fill=fg, width=2)
    draw.ellipse([x_pad - 5, y - 5, x_pad + 5, y + 5], outline=fg, width=2)

def draw_right_label(draw, x_pad, y, label, fg, bg, font):
    """Single-line label to the RIGHT of the pad (left-aligned)."""
    tw, th = text_size(font, label)
    line_start = x_pad + 6
    box_left   = line_start + 8
    box_right  = box_left + tw + HPAD * 2

    draw.rectangle([box_left, y - th // 2 - VPAD,
                    box_right + 1, y + th // 2 + VPAD],
                   fill=bg, outline=fg, width=1)
    draw.text((box_left + HPAD, y - th // 2), label, fill=fg, font=font)
    draw.line([(line_start, y), (box_left - 1, y)], fill=fg, width=2)
    draw.ellipse([x_pad - 5, y - 5, x_pad + 5, y + 5], outline=fg, width=2)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    img = Image.open(IMG_PATH).convert('RGBA')
    W, H = img.size
    print(f"Source image: {W} × {H}")

    CW = W + 2 * EXTEND
    CH = H + TITLE_H
    canvas = Image.new('RGBA', (CW, CH), (255, 255, 255, 255))
    canvas.paste(img, (EXTEND, TITLE_H), img)
    draw = ImageDraw.Draw(canvas)

    main_font  = load_font(13)
    title_font = load_font(17)
    gp_font    = load_font(10)   # kept for legend only

    spacing = (Y_LAST - Y_FIRST) / (N_PINS - 1)

    def pin_y(i):
        return int(Y_FIRST + i * spacing) + TITLE_H

    xl = X_LEFT_PAD  + EXTEND
    xr = X_RIGHT_PAD + EXTEND

    for i, (label, grp) in enumerate(LEFT_PINS):
        draw_left_label(draw, xl, pin_y(i), label, FG[grp], BG[grp], main_font)

    for i, (label, grp) in enumerate(RIGHT_PINS):
        draw_right_label(draw, xr, pin_y(i), label, FG[grp], BG[grp], main_font)

    # Title
    title = 'Raspberry Pi Pico 2 (RP2350)  —  INAV Option C Pin Assignment'
    tw, th = text_size(title_font, title)
    draw.text(((CW - tw) // 2, (TITLE_H - th) // 2),
              title, fill='#111111', font=title_font)

    # Legend
    groups = [('UART', 'uart'), ('SPI', 'spi'), ('Motor', 'motor'),
              ('Servo/dual-use', 'servo'), ('I2C', 'i2c'),
              ('ADC', 'adc'), ('LED', 'led'), ('Power/GND', 'power'), ('Other', 'other')]
    lx, ly = 10, CH - 28
    for name, grp in groups:
        lw, lh = text_size(gp_font, name)
        draw.rectangle([lx, ly, lx + lw + 10, ly + lh + 6],
                       fill=BG[grp], outline=FG[grp], width=1)
        draw.text((lx + 5, ly + 3), name, fill=FG[grp], font=gp_font)
        lx += lw + 18

    out = canvas.convert('RGB')
    out.save(OUT_PATH, 'PNG', dpi=(150, 150))
    print(f"Saved: {OUT_PATH}  ({out.size[0]} × {out.size[1]})")

if __name__ == '__main__':
    main()
