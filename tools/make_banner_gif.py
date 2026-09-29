# -*- coding: utf-8 -*-
"""
banner（GIF）—— C 方向：深色暖底 + 花里胡哨 + 流动波浪渐变名字。

设计取舍记录
------------
用户反馈原版「AI 感重、要素太少、太简洁」，且点名要：
  · 名字的桃红→橙金暖色渐变
  · 名字加粗、放大
  · 院校/专业/技术这些信息胶囊要更大更醒目
  · 整体要"花里胡哨"、元素多

之前一直做减法（留白、统一色系、克制）——那恰恰是 AI 生成感的主要来源。
这一版反过来：多层光晕 + 星光 + 等高线 + 彩色胶囊，靠"丰富"而不是"统一"取胜。

为什么必须是 GIF
---------------
Chrome 在把 SVG 当 <img> 渲染时（GitHub README 场景）不执行 SMIL 动画，
实测三种方案全空白。所以"流动"只能做成 GIF。
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

W, H = 1000, 250
FRAMES = 18
FDIR = r"C:\Windows\Fonts"
SERIF_B = os.path.join(FDIR, "BOD_B.TTF")     # Bodoni MT Bold —— 名字主字体，加粗
SCRIPT = os.path.join(FDIR, "segoesc.ttf")     # Segoe Script —— 姓氏，手写连笔
SERIF_I = os.path.join(FDIR, "BOD_I.TTF")
CJK_B = os.path.join(FDIR, "msyhbd.ttc")      # 微软雅黑 Bold —— 胶囊文字，加大加粗

# ── 底色：深紫红 → 暖酒红 ──
BG_T = (26, 15, 33)
BG_B = (78, 40, 48)

# ── 名字色带：桃红 → 橙金 ──
WARM = np.zeros((256, 3))
_stops = [(0.00, (255, 138, 143)),   # 桃红
          (0.30, (255, 176, 122)),
          (0.52, (255, 233, 192)),   # 近白暖高光（波峰）
          (0.74, (255, 197, 108)),   # 橙金
          (1.00, (242, 138, 58))]    # 深橘
for _i in range(256):
    _t = _i / 255
    for _j in range(len(_stops) - 1):
        _p0, _c0 = _stops[_j]
        _p1, _c1 = _stops[_j + 1]
        if _p0 <= _t <= _p1:
            _k = (_t - _p0) / (_p1 - _p0)
            _k = _k * _k * (3 - 2 * _k)
            WARM[_i] = [_c0[m] + (_c1[m] - _c0[m]) * _k for m in range(3)]
            break
    else:
        WARM[_i] = _stops[-1][1]

# 胶囊：四种暖/亮色，让"要素多"看起来是有设计而不是堆砌
CHIPS = [("中国地质大学（武汉）", (96, 44, 46)),
         ("地理信息工程 · 硕士在读", (118, 56, 40)),
         ("Python / Java / Vue", (48, 62, 96)),
         ("Wuhan · China", (46, 78, 62))]


def wave(phase, amp=0.13, freq=4.0):
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
    """名字：Haoyi（Bodoni Bold，加粗放大）+ Wang（手写体），整块居中。"""
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


# 星光：固定位置 + 各自的闪烁相位，逐帧变透明度 -> 真的会"眨眼"
_rng = np.random.default_rng(11)
STARS = [(float(_rng.uniform(12, W - 12)), float(_rng.uniform(10, H - 12)),
          float(_rng.uniform(1.3, 3.4)), float(_rng.uniform(0, 1)))
         for _ in range(46)]


def build(fname):
    base = vgrad(BG_T, BG_B)
    mask = name_mask()
    f_sub = ImageFont.truetype(SERIF_B, 15)
    f_chip = ImageFont.truetype(CJK_B, 15)
    t = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    chip_w = [int(t.textlength(c, font=f_chip) + 42) for c, _ in CHIPS]
    chip_total = sum(chip_w) + 10 * (len(CHIPS) - 1)

    frames = []
    for fi in range(FRAMES):
        ph = fi / FRAMES
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")

        # 三层光晕（错开呼吸，制造层次）
        d.ellipse([-150, -90, 320, 210], fill=(255, 138, 118, 46))
        d.ellipse([700, 80, 1090, 330], fill=(255, 198, 118, 42))
        d.ellipse([400, 40, 640, 250], fill=(255, 168, 200, 26))

        # 等高线（两处）
        for pts in topo(180, 128, 78, 1.0, 4):
            d.line(pts + [pts[0]], fill=(255, 205, 168, 78), width=2, joint="curve")
        for pts in topo(840, 128, 72, 2.3, 3):
            d.line(pts + [pts[0]], fill=(255, 224, 186, 58), width=2, joint="curve")

        # 星光：逐帧闪烁
        for (x, y, r, off) in STARS:
            a = 0.35 + 0.65 * abs(math.sin(math.pi * (ph + off)))
            c = (255, 236, 200, int(235 * a))
            d.line([(x - r, y), (x + r, y)], fill=c, width=1)
            d.line([(x, y - r), (x, y + r)], fill=c, width=1)
            d.ellipse([x - .6, y - .6, x + .6, y + .6], fill=c)

        # 名字背光
        d.ellipse([100, 8, 900, 222], fill=BG_T + (168,))
        img.paste(Image.fromarray(wave(ph).astype(np.uint8), "RGB"), (0, 0), mask)

        # 副标题
        d.line([(W / 2 - 250, 150), (W / 2 + 250, 150)], fill=(255, 200, 160, 95), width=1)
        d.text((W / 2, 170), "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E",
               font=f_sub, fill=(255, 224, 200), anchor="mm")

        # 胶囊：加大、加粗、四色
        x = int(W / 2 - chip_total / 2)
        for (txt, col), w in zip(CHIPS, chip_w):
            d.rounded_rectangle([x, 192, x + w, 230], radius=19,
                                fill=col + (240,), outline=(255, 202, 162, 175), width=2)
            d.text((x + w / 2, 211), txt, font=f_chip, fill=(255, 228, 208), anchor="mm")
            x += w + 10

        # 底部强调线 + 扫光
        d.rectangle([0, H - 6, W, H - 2], fill=(255, 175, 112, 230))
        sx = int(-240 + (W + 240) * ph)
        d.rectangle([sx, H - 8, sx + 240, H - 1], fill=(255, 226, 178, 235))

        frames.append(img)

    sample = Image.new("RGB", (W, H * 2))
    for i in range(2):
        sample.paste(frames[i], (0, H * i))
    pal = sample.quantize(colors=200, method=Image.MEDIANCUT)
    pf = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
    p = os.path.join(OUT, fname)
    pf[0].save(p, save_all=True, append_images=pf[1:],
               duration=130, loop=0, optimize=True, disposal=2)
    return p


def main():
    p = build("banner-dark.gif")
    print("wrote %-22s %8.1f KB" % ("banner-dark.gif", os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()
