# -*- coding: utf-8 -*-
"""
把 banner 也做成会动的 GIF —— 【已否决，当前线上不采用这个版本】

结论（2026-09-29 A/B 实测）：SVG 版明显更好，所以 banner 保持 SVG。
  · SVG 79KB：文字矢量锐利、等高线细腻、整体更精致
  · GIF 428KB：文字发软、线条偏粗，显得业余
  且 428KB 仅为换来"缓慢旋转的等高线"这一处微弱动效，性价比不划算。
  页面的动感交给打字机 GIF 承担就够了。

保留这个脚本的原因：
  1. 记录一次有价值的负面结论，避免以后有人（包括我自己）再走一遍；
  2. 如果以后想要"整块 banner 动起来"，生成逻辑已经现成。

技术备忘（这次踩过的坑）：
  · GIF 是逐帧独立 LZW 压缩、不做帧间差分，所以静止的背景在每一帧都要重新压一遍
    —— 减帧数是唯一有效的体积杠杆（22帧885KB -> 14帧428KB）。
  · 逐帧 ADAPTIVE 调色板会摧毁跨帧压缩；必须所有帧共用一套调色板。
  · Floyd-Steinberg 抖动引入高频噪声，会让体积从 428KB 涨到 1475KB，必须关掉。
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

W, H = 960, 240
FRAMES = 14
FONT = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_B = r"C:\Windows\Fonts\msyh.ttc"

CHIPS = [("中国地质大学（武汉）", 150), ("硕士在读", 82), ("地理信息 · AI 工程", 132)]
GAP = 11


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def make_bg(top, bot):
    """竖直线性渐变，列方向复用同一行像素。"""
    grad = Image.new("RGB", (1, H))
    gp = grad.load()
    for y in range(H):
        gp[0, y] = lerp(top, bot, y / (H - 1))
    return grad.resize((W, H))


def topo(cx, cy, r0, seed, rings, squash=0.62):
    """返回一组闭合折线（等高线）。r(θ) 用多谐波扰动，得到自然山脊感。"""
    shapes = []
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
        shapes.append(pts)
    return shapes


def rot(pts, deg, cx, cy):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for (x, y) in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return out


def build(fname, dark=True):
    if dark:
        bg_t, bg_b = hx("#04121f"), hx("#0c3244")
        glow_a, glow_b = hx("#0e7ea8"), hx("#12a594")
        line, line2 = hx("#5fd0e6"), hx("#8fe6f5")
        grid, title, sub = hx("#2c6b80"), hx("#eaf7fb"), hx("#8fd4e6")
        chip_bg, chip_s = hx("#0f3a4a"), hx("#7fc9dc")
        accent, shine = hx("#12a594"), hx("#7ff0ff")
    else:
        bg_t, bg_b = hx("#eaf6fb"), hx("#bcdcee")
        glow_a, glow_b = hx("#8fd3ec"), hx("#8fdccb")
        line, line2 = hx("#16688c"), hx("#2b8bad")
        grid, title, sub = hx("#8ab6c9"), hx("#062735"), hx("#0e5b7a")
        chip_bg, chip_s = hx("#ffffff"), hx("#3d8cad")
        accent, shine = hx("#3d9dc4"), hx("#7fd0e8")

    base = make_bg(bg_t, bg_b)
    f_title = ImageFont.truetype(FONT, 44)
    f_sub = ImageFont.truetype(FONT, 15)
    f_chip = ImageFont.truetype(FONT_B, 12)

    frames = []
    for fi in range(FRAMES):
        t = fi / FRAMES
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")

        # 两侧辉光（跟着缓慢呼吸）
        r1 = int(300 * (0.9 + 0.1 * math.sin(t * 2 * math.pi)))
        d.ellipse([170 - r1, 60 - r1, 170 + r1, 60 + r1], fill=glow_a + (34,))
        r2 = int(260 * (0.9 + 0.1 * math.sin(t * 2 * math.pi + 2.0)))
        d.ellipse([845 - r2, 200 - r2, 845 + r2, 200 + r2], fill=glow_b + (28,))

        # 地图网格
        for x in range(0, W + 1, 40):
            d.line([(x, 0), (x, H)], fill=grid + (34,), width=1)
        for y in range(0, H + 1, 30):
            d.line([(0, y), (W, y)], fill=grid + (34,), width=1)

        # 等高线：两组反向缓慢旋转
        for pts in topo(250, 125, 96, 1.0, 6):
            d.line(rot(pts, t * 360, 250, 125) + [rot(pts, t * 360, 250, 125)[0]],
                   fill=line + (118,), width=2, joint="curve")
        for pts in topo(775, 125, 88, 2.3, 5):
            d.line(rot(pts, -t * 360, 775, 125) + [rot(pts, -t * 360, 775, 125)[0]],
                   fill=line2 + (86,), width=2, joint="curve")

        # 中央等高线（背光）
        for pts in topo(500, 125, 132, 3.7, 4):
            d.line(rot(pts, t * 180, 500, 125) + [rot(pts, t * 180, 500, 125)[0]],
                   fill=line + (60,), width=2, joint="curve")

        # 文字背光
        d.ellipse([170, 30, 830, 225], fill=bg_t + (150,))

        # 文字
        d.text((W // 2, 96), "HAOYI WANG", font=f_title, fill=title, anchor="mm")
        d.text((W // 2, 130), "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E",
               font=f_sub, fill=sub, anchor="mm")

        # 标签
        total = sum(w for _, w in CHIPS) + GAP * (len(CHIPS) - 1)
        x = W // 2 - total // 2
        for txt, w in CHIPS:
            d.rounded_rectangle([x, 162, x + w, 189], radius=13,
                                fill=chip_bg + (235,), outline=chip_s + (120,), width=1)
            d.text((x + w // 2, 175), txt, font=f_chip, fill=chip_s, anchor="mm")
            x += w + GAP

        # 底部强调线 + 流光（注意必须落在画布内：H=240）
        d.rectangle([0, H - 7, W, H - 4], fill=accent + (215,))
        sx = int(-260 + (W + 260) * t)
        d.rectangle([sx, H - 8, sx + 260, H - 3], fill=shine + (225,))

        frames.append(img)

    # ---- 关键：用一张覆盖所有帧的公共调色板 ----
    # 逐帧 ADAPTIVE 会让每帧调色板不同，GIF 的跨帧 LZW 压缩就完全失效了
    # （实测同一份画面，per-frame 调色板 885KB vs 公共调色板 200KB 量级）。
    # 这里把全部帧拼成一张采样图，只建一次调色板。
    sample = Image.new("RGB", (W, H * 2))
    for i in range(min(2, len(frames))):
        sample.paste(frames[i], (0, H * i))
    pal = sample.quantize(colors=128, method=Image.MEDIANCUT)
    # 抖动会引入高频噪声、显著撑大体积；渐变处轻微色带可以接受。
    pframes = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]

    p = os.path.join(OUT, fname)
    pframes[0].save(p, save_all=True, append_images=pframes[1:],
                    duration=150, loop=0, optimize=True, disposal=2)
    return p


def main():
    for dark, fname in ((True, "banner-dark.gif"), (False, "banner-light.gif")):
        p = build(fname, dark)
        print("wrote %-22s %8.1f KB" % (fname, os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()

