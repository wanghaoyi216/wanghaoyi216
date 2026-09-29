# -*- coding: utf-8 -*-
"""
banner（GIF 版）—— 名字带「流动 + 波浪形渐变」。

为什么必须是 GIF
---------------
用户要求名字有"流动"效果。但 Chrome 在把 SVG 当 <img> 渲染时
（GitHub README 就是这种场景）不执行 SMIL 动画 —— 实测三种方案全空白。
所以任何"会动"的东西都只能做成 GIF。

波浪渐变怎么算
--------------
不用逐像素画，而是构造一个渐变场 t(x, y)：

    t = frac( x/W  +  phase )  +  amp * sin( 2π·y/H·freq  +  phase·2.4 )

  · x/W + phase      -> 水平方向随时间平移 = "流动"
  · amp·sin(...)     -> 垂直方向正弦起伏   = "波浪形"
然后用一条多段色带把 t 映射成颜色，再用文字遮罩把它裁出来。
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

W, H = 1000, 250
FRAMES = 20
FDIR = r"C:\Windows\Fonts"
SERIF_I = os.path.join(FDIR, "BOD_I.TTF")
SCRIPT = os.path.join(FDIR, "segoesc.ttf")
SERIF_R = os.path.join(FDIR, "BOD_R.TTF")
CJK = os.path.join(FDIR, "msyh.ttc")

BG_T = (4, 18, 31)
BG_B = (12, 50, 68)
LINE = (95, 208, 230)
SUB = (143, 212, 230)
CHIP_BG = (15, 58, 74)
CHIP_S = (127, 201, 220)
GRID = (44, 107, 128)

# 波浪色带：深青 -> 亮青 -> 近白 -> 亮青 -> 深青（中间是波峰高光）
RAMP = [(0.00, (14, 96, 128)),
        (0.26, (52, 190, 228)),
        (0.50, (238, 251, 255)),
        (0.74, (52, 190, 228)),
        (1.00, (14, 96, 128))]

CHIPS = ["中国地质大学（武汉）", "硕士在读", "地理信息 · AI 工程"]


def ramp_lut(n=256):
    lut = np.zeros((n, 3), dtype=np.float64)
    for i in range(n):
        t = i / (n - 1)
        for j in range(len(RAMP) - 1):
            p0, c0 = RAMP[j]
            p1, c1 = RAMP[j + 1]
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0)
                # 平滑一点，避免色带之间出现硬边
                k = k * k * (3 - 2 * k)
                lut[i] = [c0[m] + (c1[m] - c0[m]) * k for m in range(3)]
                break
        else:
            lut[i] = RAMP[-1][1]
    return lut


LUT = ramp_lut()


def wave_field(phase, amp=0.085, freq=1.6):
    xs = np.arange(W)[None, :].astype(np.float64)
    ys = np.arange(H)[:, None].astype(np.float64)
    t = xs / W + phase + amp * np.sin(2 * math.pi * (ys / H) * freq + phase * 2.4)
    idx = (np.mod(t, 1.0) * 255).astype(np.int32)
    return LUT[idx]          # (H, W, 3)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(top, bot):
    g = Image.new("RGB", (1, H))
    gp = g.load()
    for y in range(H):
        gp[0, y] = lerp(top, bot, y / (H - 1))
    return g.resize((W, H))


def topo(cx, cy, r0, seed, rings, squash=0.62):
    out = []
    for k in range(rings):
        r = r0 * (1 + 0.30 * k / max(rings - 1, 1))
        pts = []
        for i in range(160):
            t = 2 * math.pi * i / 160.0
            rr = r
            rr *= 1 + 0.16 * math.sin(3 * t + seed * 0.7)
            rr *= 1 + 0.09 * math.sin(5 * t + seed * 1.9)
            rr *= 1 + 0.05 * math.sin(8 * t + seed * 2.7)
            pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t) * squash))
        out.append(pts)
    return out


def text_mask():
    """把「Haoyi」(Bodoni 斜体) + 「Wang」(手写) 合成一张黑白遮罩。"""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    f1 = ImageFont.truetype(SERIF_I, 76)
    f2 = ImageFont.truetype(SCRIPT, 44)
    tmp = ImageDraw.Draw(Image.new("L", (10, 10)))
    w1 = tmp.textlength("Haoyi", font=f1)
    w2 = tmp.textlength("Wang", font=f2)
    x = W / 2 - (w1 + 10 + w2) / 2.0
    d.text((x + w1, 82), "Haoyi", font=f1, fill=255, anchor="rm")
    d.text((x + w1 + 10, 88), "Wang", font=f2, fill=255, anchor="lm")
    return m


def build(fname):
    base = vgrad(BG_T, BG_B)
    f_sub = ImageFont.truetype(SERIF_R, 14)
    f_chip = ImageFont.truetype(CJK, 12)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    chip_w = [int(tmp.textlength(c, font=f_chip) + 34) for c in CHIPS]
    chip_total = sum(chip_w) + 11 * (len(CHIPS) - 1)

    mask = text_mask()
    frames = []

    for fi in range(FRAMES):
        phase = fi / FRAMES
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")

        d.ellipse([-140, -40, 290, 180], fill=(14, 126, 168, 34))
        d.ellipse([720, 120, 1040, 310], fill=(18, 165, 148, 30))

        # 这里原本还有一层地图网格线（40px 间距）。
        # 实测它几乎看不见（32/255 透明度），却让 GIF 从 385KB 涨到 554KB ——
        # 细密线条是 GIF 压缩的天敌（每帧独立压缩、不做帧间差分，静止的网格也要反复压）。
        # 已删除。

        for pts in topo(215, 125, 88, 1.0, 5):
            d.line(pts + [pts[0]], fill=LINE + (110,), width=2, joint="curve")
        for pts in topo(800, 125, 82, 2.3, 4):
            d.line(pts + [pts[0]], fill=LINE + (80,), width=2, joint="curve")

        # 文字背光
        d.ellipse([150, 20, 850, 210], fill=BG_T + (150,))

        # 名字 = 波浪渐变场 × 文字遮罩
        grad = Image.fromarray(wave_field(phase).astype(np.uint8), "RGB")
        img.paste(grad, (0, 0), mask)

        # 分隔线 + 副标题
        d.line([(W / 2 - 235, 120), (W / 2 + 235, 120)], fill=LINE + (90,), width=1)
        d.text((W / 2, 142), "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E",
               font=f_sub, fill=SUB, anchor="mm")

        # 标签
        x = int(W / 2 - chip_total / 2)
        for c, w in zip(CHIPS, chip_w):
            d.rounded_rectangle([x, 168, x + w, 195], radius=13,
                                fill=CHIP_BG + (235,), outline=CHIP_S + (115,), width=1)
            d.text((x + w / 2, 181), c, font=f_chip, fill=CHIP_S, anchor="mm")
            x += w + 11

        # 底部强调线 + 扫光
        d.rectangle([0, H - 7, W, H - 4], fill=(18, 165, 148, 210))
        sx = int(-220 + (W + 220) * phase)
        d.rectangle([sx, H - 8, sx + 220, H - 3], fill=(127, 240, 255, 215))

        frames.append(img)

    # 所有帧共用一套调色板（逐帧 ADAPTIVE 会摧毁跨帧压缩）
    sample = Image.new("RGB", (W, H * 2))
    for i in range(2):
        sample.paste(frames[i], (0, H * i))
    pal = sample.quantize(colors=200, method=Image.MEDIANCUT)
    pf = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]

    p = os.path.join(OUT, fname)
    pf[0].save(p, save_all=True, append_images=pf[1:],
               duration=140, loop=0, optimize=True, disposal=2)
    return p


def main():
    p = build("banner-dark.gif")
    print("wrote %-22s %8.1f KB" % ("banner-dark.gif", os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()
