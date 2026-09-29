# -*- coding: utf-8 -*-
"""
banner 风格样张：三种完全不同的方向，供用户直接挑。

A 深色 + 暖色渐变名字      —— 保留克制底子，只换名字的色温
B 奶油浅底 + 粉金渐变      —— 整体换暖，最"可爱"
C 深色 + 花里胡哨          —— 加星光/光斑/装饰层，元素最多
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "preview")
os.makedirs(OUT, exist_ok=True)

W, H = 1000, 250
FDIR = r"C:\Windows\Fonts"
BOD_B = os.path.join(FDIR, "BOD_B.TTF")
BOD_I = os.path.join(FDIR, "BOD_I.TTF")
SCRIPT = os.path.join(FDIR, "segoesc.ttf")
COMIC_B = os.path.join(FDIR, "COMICBD.TTF")
COMIC = os.path.join(FDIR, "comic.ttf")
YAHEI_B = os.path.join(FDIR, "msyhbd.ttc")
YAHEI = os.path.join(FDIR, "msyh.ttc")


def lut(stops, n=256):
    o = np.zeros((n, 3))
    for i in range(n):
        t = i / (n - 1)
        for j in range(len(stops) - 1):
            p0, c0 = stops[j]
            p1, c1 = stops[j + 1]
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0)
                k = k * k * (3 - 2 * k)
                o[i] = [c0[m] + (c1[m] - c0[m]) * k for m in range(3)]
                break
        else:
            o[i] = stops[-1][1]
    return o


# ── 桃红 -> 橙金 暖色带 ──
WARM = lut([(0.00, (255, 138, 143)),   # 桃红
            (0.30, (255, 175, 120)),
            (0.52, (255, 232, 190)),   # 近白暖高光
            (0.74, (255, 196, 107)),   # 橙金
            (1.00, (240, 138, 60))])   # 深橘


def wave(phase, amp=0.10, freq=4.5):
    xs = np.arange(W)[None, :].astype(float)
    ys = np.arange(H)[:, None].astype(float)
    t = xs / W + phase + amp * np.sin(2 * math.pi * (ys / H) * freq + phase * 2.4)
    return WARM[(np.mod(t, 1.0) * 255).astype(np.int32)]


def vgrad(top, bot):
    a = np.zeros((H, W, 3))
    for y in range(H):
        k = y / (H - 1)
        a[y, :, :] = [top[m] + (bot[m] - top[m]) * k for m in range(3)]
    return Image.fromarray(a.astype(np.uint8), "RGB")


def topo(cx, cy, r0, seed, rings, squash=0.62):
    out = []
    for k in range(rings):
        r = r0 * (1 + 0.30 * k / max(rings - 1, 1))
        pts = []
        for i in range(160):
            t = 2 * math.pi * i / 160.0
            rr = r * (1 + .16 * math.sin(3 * t + seed * .7)) * (1 + .09 * math.sin(5 * t + seed * 1.9)) \
                 * (1 + .05 * math.sin(8 * t + seed * 2.7))
            pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t) * squash))
        out.append(pts)
    return out


def name_mask(font_a, font_b, size_a, size_b, y):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    t = ImageDraw.Draw(Image.new("L", (10, 10)))
    w1 = t.textlength("Haoyi", font=font_a)
    w2 = t.textlength("Wang", font=font_b)
    x = W / 2 - (w1 + 8 + w2) / 2
    d.text((x + w1, y), "Haoyi", font=font_a, fill=255, anchor="rm")
    d.text((x + w1 + 8, y + 4), "Wang", font=font_b, fill=255, anchor="lm")
    return m


def sparkle(d, rng, n, box, color, rmin=1.5, rmax=3.2):
    for _ in range(n):
        x = rng.uniform(box[0], box[1])
        y = rng.uniform(box[2], box[3])
        r = rng.uniform(rmin, rmax)
        d.line([(x - r, y), (x + r, y)], fill=color, width=1)
        d.line([(x, y - r), (x, y + r)], fill=color, width=1)


# ────────────────────────────────────────────── A
def build_A():
    base = vgrad((28, 18, 32), (66, 36, 40))     # 暖调深底
    img = base.copy()
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([-120, -60, 300, 180], fill=(255, 150, 110, 40))
    d.ellipse([720, 110, 1060, 320], fill=(255, 190, 120, 36))
    for pts in topo(200, 125, 82, 1.0, 4):
        d.line(pts + [pts[0]], fill=(255, 190, 150, 70), width=2, joint="curve")
    d.ellipse([140, 16, 860, 214], fill=(28, 18, 32, 150))
    mask = name_mask(ImageFont.truetype(BOD_B, 84), ImageFont.truetype(SCRIPT, 48), 84, 48, 108)
    img.paste(Image.fromarray(wave(0.22).astype(np.uint8), "RGB"), (0, 0), mask)
    f_sub = ImageFont.truetype(BOD_B, 15)
    f_chip = ImageFont.truetype(YAHEI_B, 15)
    d.text((W / 2, 156), "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E",
           font=f_sub, fill=(255, 214, 190), anchor="mm")
    chips = ["中国地质大学（武汉）", "地理信息工程 · 硕士在读", "Python / Java / Vue"]
    t = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    ws = [int(t.textlength(c, font=f_chip) + 44) for c in chips]
    tot = sum(ws) + 12 * (len(ws) - 1)
    x = int(W / 2 - tot / 2)
    for c, w in zip(chips, ws):
        d.rounded_rectangle([x, 182, x + w, 218], radius=18,
                            fill=(88, 48, 46, 235), outline=(255, 175, 130, 150), width=2)
        d.text((x + w / 2, 200), c, font=f_chip, fill=(255, 214, 190), anchor="mm")
        x += w + 12
    d.rectangle([0, H - 6, W, H - 2], fill=(255, 170, 110, 220))
    return img


# ────────────────────────────────────────────── B
def build_B():
    base = vgrad((255, 246, 235), (255, 224, 205))
    img = base.copy()
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([-120, -60, 300, 180], fill=(255, 205, 175, 90))
    d.ellipse([720, 110, 1060, 320], fill=(255, 225, 180, 90))
    for pts in topo(200, 125, 82, 1.0, 4):
        d.line(pts + [pts[0]], fill=(232, 150, 130, 70), width=2, joint="curve")
    rng = np.random.default_rng(7)
    sparkle(d, rng, 26, (20, W - 20, 16, 234), (240, 160, 140, 200))
    d.ellipse([150, 22, 850, 200], fill=(255, 246, 235, 190))
    mask = name_mask(ImageFont.truetype(BOD_B, 84), ImageFont.truetype(SCRIPT, 48), 84, 48, 108)
    img.paste(Image.fromarray(wave(0.22).astype(np.uint8), "RGB"), (0, 0), mask)
    f_sub = ImageFont.truetype(BOD_B, 15)
    f_chip = ImageFont.truetype(YAHEI_B, 15)
    d.text((W / 2, 156), "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E",
           font=f_sub, fill=(186, 104, 88), anchor="mm")
    chips = ["中国地质大学（武汉）", "地理信息工程 · 硕士在读", "Python / Java / Vue"]
    t = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    ws = [int(t.textlength(c, font=f_chip) + 44) for c in chips]
    tot = sum(ws) + 12 * (len(ws) - 1)
    x = int(W / 2 - tot / 2)
    for c, w in zip(chips, ws):
        d.rounded_rectangle([x, 182, x + w, 218], radius=18,
                            fill=(255, 255, 255, 245), outline=(245, 170, 150, 220), width=2)
        d.text((x + w / 2, 200), c, font=f_chip, fill=(196, 108, 92), anchor="mm")
        x += w + 12
    d.rectangle([0, H - 6, W, H - 2], fill=(246, 150, 130, 220))
    return img


# ────────────────────────────────────────────── C
def build_C():
    base = vgrad((24, 14, 30), (74, 38, 46))
    img = base.copy()
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([-140, -80, 320, 200], fill=(255, 140, 120, 48))
    d.ellipse([700, 90, 1080, 330], fill=(255, 200, 120, 44))
    d.ellipse([420, 60, 620, 240], fill=(255, 170, 200, 26))
    for pts in topo(190, 125, 78, 1.0, 4):
        d.line(pts + [pts[0]], fill=(255, 200, 160, 80), width=2, joint="curve")
    for pts in topo(830, 125, 72, 2.3, 3):
        d.line(pts + [pts[0]], fill=(255, 220, 180, 60), width=2, joint="curve")
    rng = np.random.default_rng(11)
    sparkle(d, rng, 40, (16, W - 16, 14, 236), (255, 235, 200, 230), 1.4, 3.6)
    for (cx, cy, r, c) in ((120, 60, 4, (255, 200, 150, 220)), (900, 190, 3, (255, 170, 190, 220)),
                           (640, 40, 2.4, (255, 230, 190, 210)), (300, 210, 2.2, (255, 190, 210, 200))):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    d.ellipse([120, 10, 880, 220], fill=(24, 14, 30, 165))
    mask = name_mask(ImageFont.truetype(BOD_B, 88), ImageFont.truetype(SCRIPT, 50), 88, 50, 106)
    img.paste(Image.fromarray(wave(0.22, amp=0.13, freq=4.0).astype(np.uint8), "RGB"), (0, 0), mask)
    f_sub = ImageFont.truetype(BOD_B, 15)
    f_chip = ImageFont.truetype(YAHEI_B, 15)
    d.text((W / 2, 158), "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E",
           font=f_sub, fill=(255, 220, 195), anchor="mm")
    chips = ["中国地质大学（武汉）", "地理信息工程 · 硕士", "Python / Java / Vue", "Wuhan · China"]
    t = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    ws = [int(t.textlength(c, font=f_chip) + 40) for c in chips]
    tot = sum(ws) + 10 * (len(ws) - 1)
    x = int(W / 2 - tot / 2)
    cols = [(92, 46, 48), (112, 58, 40), (52, 60, 92), (60, 74, 60)]
    for (c, w), col in zip(zip(chips, ws), cols):
        d.rounded_rectangle([x, 182, x + w, 220], radius=19, fill=col + (235,),
                            outline=(255, 200, 160, 170), width=2)
        d.text((x + w / 2, 201), c, font=f_chip, fill=(255, 226, 205), anchor="mm")
        x += w + 10
    d.rectangle([0, H - 6, W, H - 2], fill=(255, 175, 115, 230))
    return img


def main():
    items = [("A  深色底 + 暖色渐变名字", build_A),
             ("B  奶油浅底 + 粉金渐变（最可爱）", build_B),
             ("C  深色 + 花里胡哨（元素最多）", build_C)]
    ims = []
    for name, fn in items:
        im = fn()
        im.save(os.path.join(OUT, "style_%s.png" % name[0]))
        ims.append((name, im))
        print("  %s" % name)
    sheet = Image.new("RGB", (W, (H + 26) * len(ims)), (12, 12, 14))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(YAHEI, 14)
    for i, (n, im) in enumerate(ims):
        y = i * (H + 26)
        d.text((8, y + 6), n, font=f, fill=(220, 220, 228))
        sheet.paste(im, (0, y + 26))
    sheet.save(os.path.join(OUT, "style-sheet.png"))
    print("sheet -> preview/style-sheet.png")


if __name__ == "__main__":
    main()
