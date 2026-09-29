# -*- coding: utf-8 -*-
"""
banner（GIF）—— 名字带「流动 + 波浪形渐变」+ 星光闪烁。
配色全部来自 tools/theme.py，可在多套主题间切换。

为什么必须是 GIF
---------------
Chrome 在把 SVG 当 <img> 渲染时（GitHub README 场景）不执行 SMIL 动画，
实测三种方案（textPath 动画 d / clipPath width / opacity 轮播）全部变空白。
所以"会动"只能做成 GIF。
"""
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = r"C:\Windows\Fonts"
SERIF_B = os.path.join(FDIR, "BOD_B.TTF")
SCRIPT = os.path.join(FDIR, "segoesc.ttf")
CJK_B = os.path.join(FDIR, "msyhbd.ttc")

W, H = 1000, 250
FRAMES = 18

# 胶囊文案（与主题无关）
CHIP_TEXT = ["中国地质大学（武汉）", "地理信息工程 · 硕士在读",
             "Python / Java / Vue", "Wuhan · China"]


def wave(lut, phase, amp=0.13, freq=4.0):
    xs = np.arange(W)[None, :].astype(float)
    ys = np.arange(H)[:, None].astype(float)
    t = xs / W + phase + amp * np.sin(2 * math.pi * (ys / H) * freq + phase * 2.4)
    return lut[(np.mod(t, 1.0) * 255).astype(np.int32)]


def vgrad(top, bot):
    a = np.zeros((H, W, 3))
    for y in range(H):
        k = y / (H - 1)
        a[y, :, :] = [top[m] + (bot[m] - top[m]) * k for m in range(3)]
    return Image.fromarray(a.astype(np.uint8), "RGB")


def topo(cx, cy, r0, seed, rings, squash=0.62):
    out = []
    for k in range(rings):
        r = r0 * (1 + 0.32 * k / max(rings - 1, 1))
        pts = []
        for i in range(160):
            t = 2 * math.pi * i / 160.0
            rr = r * (1 + .16 * math.sin(3 * t + seed * .7)) * (1 + .09 * math.sin(5 * t + seed * 1.9)) \
                 * (1 + .05 * math.sin(8 * t + seed * 2.7))
            pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t) * squash))
        out.append(pts)
    return out


def name_mask():
    fa = ImageFont.truetype(SERIF_B, 88)
    fb = ImageFont.truetype(SCRIPT, 50)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    t = ImageDraw.Draw(Image.new("L", (10, 10)))
    w1 = t.textlength("Haoyi", font=fa)
    w2 = t.textlength("Wang", font=fb)
    x = W / 2 - (w1 + 8 + w2) / 2
    d.text((x + w1, 104), "Haoyi", font=fa, fill=255, anchor="rm")
    d.text((x + w1 + 8, 110), "Wang", font=fb, fill=255, anchor="lm")
    return m


def build(theme_name, out_path):
    th = T.get(theme_name)
    lut = T.name_lut(th)
    base = vgrad(T.hx(th["bg"][0]), T.hx(th["bg"][1]))
    mask = name_mask()
    f_sub = ImageFont.truetype(SERIF_B, 15)
    f_chip = ImageFont.truetype(CJK_B, 15)
    t = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    chip_w = [int(t.textlength(c, font=f_chip) + 42) for c in CHIP_TEXT]
    chip_total = sum(chip_w) + 10 * (len(CHIP_TEXT) - 1)

    g0, g1, g2 = [T.hx(c) for c in th["glows"]]
    contour = T.hx(th["contour"])
    star = T.hx(th["star"])
    sub_c = T.hx(th["sub"])
    chip_txt = T.hx(th["chip_text"])
    accent = T.hx(th["accent"])
    bg_t = T.hx(th["bg"][0])

    rng = np.random.default_rng(11)
    STARS = [(float(rng.uniform(12, W - 12)), float(rng.uniform(10, H - 12)),
              float(rng.uniform(1.3, 3.4)), float(rng.uniform(0, 1))) for _ in range(46)]

    frames = []
    for fi in range(FRAMES):
        ph = fi / FRAMES
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse([-150, -90, 320, 210], fill=g0 + (46,))
        d.ellipse([700, 80, 1090, 330], fill=g1 + (42,))
        d.ellipse([400, 40, 640, 250], fill=g2 + (26,))
        for pts in topo(180, 128, 78, 1.0, 4):
            d.line(pts + [pts[0]], fill=contour + (78,), width=2, joint="curve")
        for pts in topo(840, 128, 72, 2.3, 3):
            d.line(pts + [pts[0]], fill=contour + (58,), width=2, joint="curve")
        for (x, y, r, off) in STARS:
            a = 0.35 + 0.65 * abs(math.sin(math.pi * (ph + off)))
            c = star + (int(235 * a),)
            d.line([(x - r, y), (x + r, y)], fill=c, width=1)
            d.line([(x, y - r), (x, y + r)], fill=c, width=1)
            d.ellipse([x - .6, y - .6, x + .6, y + .6], fill=c)
        d.ellipse([100, 8, 900, 222], fill=bg_t + (168,))
        img.paste(Image.fromarray(wave(lut, ph).astype(np.uint8), "RGB"), (0, 0), mask)
        d.line([(W / 2 - 250, 150), (W / 2 + 250, 150)], fill=contour + (95,), width=1)
        d.text((W / 2, 170), "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E",
               font=f_sub, fill=sub_c, anchor="mm")
        x = int(W / 2 - chip_total / 2)
        for txt, w, col in zip(CHIP_TEXT, chip_w, [T.hx(c) for c in th["chips"]]):
            d.rounded_rectangle([x, 192, x + w, 230], radius=19, fill=col + (240,),
                                outline=contour + (110,), width=2)
            d.text((x + w / 2, 211), txt, font=f_chip, fill=chip_txt, anchor="mm")
            x += w + 10
        d.rectangle([0, H - 6, W, H - 2], fill=accent + (230,))
        sx = int(-240 + (W + 240) * ph)
        d.rectangle([sx, H - 8, sx + 240, H - 1], fill=star + (235,))
        frames.append(img)

    sample = Image.new("RGB", (W, H * 2))
    for i in range(2):
        sample.paste(frames[i], (0, H * i))
    pal = sample.quantize(colors=200, method=Image.MEDIANCUT)
    pf = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pf[0].save(out_path, save_all=True, append_images=pf[1:],
               duration=130, loop=0, optimize=True, disposal=2)
    return out_path


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else T.ACTIVE
    p = os.path.join(ROOT, "assets", "themes", name, "banner.gif")
    build(name, p)
    print("  banner  %-8s %s  (%.1f KB)" % (name, p, os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()
