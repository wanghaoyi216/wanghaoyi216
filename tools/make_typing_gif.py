# -*- coding: utf-8 -*-
"""
打字机（GIF）—— 配色来自 tools/theme.py。

字体：中文 华文行楷（本身是连笔书法）、英文 Comic Sans MS Bold。
Comic Sans 没有真正的连字字形，所以用「负字距」把字母挤到一起制造连笔感。
"""
import os
import sys
import unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageColor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = r"C:\Windows\Fonts"
CJK_FONT = os.path.join(FDIR, "STXINGKA.TTF")
LATIN = os.path.join(FDIR, "COMICBD.TTF")

W, H = 780, 84
FS = 26
TRACK = -1.6          # 负字距 -> 连笔感
TYPE_F, HOLD_F, ERASE_F = 0.58, 0.16, 0.26

LINES = [
    "用 AI 解决科研和教学里的麻烦事",
    "Python / Java / Vue 全栈开发",
    "Building tools that actually run",
]

_fc = {}


def is_cjk(ch):
    return unicodedata.east_asian_width(ch) in ("W", "F")


def face(ch, size):
    k = (is_cjk(ch), size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(CJK_FONT if k[0] else LATIN, size)
    return _fc[k]


def _adv(d, ch):
    w = d.textlength(ch, font=face(ch, FS))
    return w if is_cjk(ch) or ch == " " else w + TRACK


def draw_line(d, text, cx, cy, color):
    ws = [_adv(d, c) for c in text]
    x = cx - sum(ws) / 2.0
    for ch, w in zip(text, ws):
        if ch != " ":
            d.text((x, cy), ch, font=face(ch, FS), fill=color)
        x += w
    return sum(ws)


def build(theme_name, out_path):
    color = T.get(theme_name)["typing"]
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    steps = 26
    frames = []
    for idx in range(steps * len(LINES)):
        i, k = idx // steps, idx % steps
        phase = k / steps
        line = LINES[i]
        if phase < TYPE_F:
            n = max(1, int(round(len(line) * (phase / TYPE_F))))
        elif phase < TYPE_F + HOLD_F:
            n = len(line)
        else:
            p = (phase - TYPE_F - HOLD_F) / ERASE_F
            n = max(0, int(round(len(line) * (1 - p))))
        shown = line[:n]

        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cy = (H - FS * 1.4) / 2
        sw = draw_line(d, shown, W // 2, cy, ImageColor.getrgb(color) + (255,))
        if shown:
            cx = (W + sw) / 2 + 4
            d.rectangle([cx, cy + 2, cx + 2.5, cy + FS + 4],
                        fill=ImageColor.getrgb(color) + (255,))

        alpha = img.split()[3]
        pimg = img.convert("RGB").quantize(colors=255)
        pimg.paste(255, Image.eval(alpha, lambda a: 255 if a < 128 else 0))
        pimg.info["transparency"] = 255
        frames.append(pimg)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    frames[0].save(out_path, save_all=True, append_images=frames[1:],
                   duration=70, loop=0, optimize=True, disposal=2)
    return out_path


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else T.ACTIVE
    p = os.path.join(ROOT, "assets", "themes", name, "typing.gif")
    build(name, p)
    print("  typing  %-8s %s  (%.1f KB)" % (name, p, os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()
