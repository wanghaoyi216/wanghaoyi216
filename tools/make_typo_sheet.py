# -*- coding: utf-8 -*-
"""
生成「名字排版」样张，让用户直接挑，而不是由我替他决定。

背景（渐变 + 网格 + 等高线）与线上 banner 保持一致，
这样样张里看到的就是真实效果，而不是脱离上下文的字体样本。
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "preview")

W, H = 900, 225
F = r"C:\Windows\Fonts\%s"

BODONI_B = F % "BOD_B.TTF"
BODONI_R = F % "BOD_R.TTF"
BODONI_I = F % "BOD_I.TTF"
GARA = F % "GARA.TTF"
SCRIPT = F % "segoesc.ttf"
PRINT = F % "segoepr.ttf"
INK = F % "Inkfree.ttf"
UI_B = F % "segoeuib.ttf"
UI = F % "segoeui.ttf"
MSYH = F % "msyh.ttc"

BG_T = "#04121f"
BG_B = "#0c3244"
LINE = "#5fd0e6"
GRID = "#2c6b80"
TITLE = "#eaf7fb"
SUB = "#8fd4e6"
CHIP_BG = "#0f3a4a"
CHIP_S = "#7fc9dc"
ACCENT = "#12a594"


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def background():
    top, bot = hx(BG_T), hx(BG_B)
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


def grad_text(img, xy, text, font, c1, c2, anchor="mm", spread=26):
    """用渐变填充绘制文字（先画进遮罩，再贴渐变）。"""
    d = ImageDraw.Draw(img)
    d.text(xy, text, font=font, fill=(255, 255, 255), anchor=anchor)
    g = Image.new("RGB", img.size)
    gd = ImageDraw.Draw(g)
    a, b = hx(c1), hx(c2)
    for y in range(img.size[1]):
        gd.line([(0, y), (img.size[0], y)], fill=lerp(a, b, y / (img.size[1] - 1)))
    # 只保留文字区域
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255, anchor=anchor)
    img.paste(g, (0, 0), mask)


def base_canvas():
    img = background()
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([-130, -30, 300, 190], fill=hx("#0e7ea8") + (34,))
    d.ellipse([700, 110, 1030, 310], fill=hx("#12a594") + (30,))
    for x in range(0, W + 1, 40):
        d.line([(x, 0), (x, H)], fill=hx(GRID) + (34,), width=1)
    for y in range(0, H + 1, 30):
        d.line([(0, y), (W, y)], fill=hx(GRID) + (34,), width=1)
    for pts in topo(215, 112, 88, 1.0, 6):
        d.line(pts + [pts[0]], fill=hx(LINE) + (115,), width=2, joint="curve")
    for pts in topo(700, 112, 82, 2.3, 5):
        d.line(pts + [pts[0]], fill=hx("#8fe6f5") + (85,), width=2, joint="curve")
    for pts in topo(450, 112, 120, 3.7, 4):
        d.line(pts + [pts[0]], fill=hx(LINE) + (58,), width=2, joint="curve")
    d.ellipse([150, 25, 750, 200], fill=hx(BG_T) + (150,))
    d.rectangle([0, H - 7, W, H - 4], fill=hx(ACCENT) + (215,))
    return img


def chips(d, y):
    items = [("中国地质大学（武汉）", 138), ("硕士在读", 78), ("地理信息 · AI 工程", 124)]
    gap = 10
    total = sum(w for _, w in items) + gap * (len(items) - 1)
    x = W // 2 - total // 2
    f = ImageFont.truetype(MSYH, 11)
    for t, w in items:
        d.rounded_rectangle([x, y, x + w, y + 25], radius=12,
                            fill=hx(CHIP_BG) + (235,), outline=hx(CHIP_S) + (120,), width=1)
        d.text((x + w // 2, y + 12), t, font=f, fill=hx(CHIP_S), anchor="mm")
        x += w + gap


# ---------------------------------------------------------------- 四种排版

def v_a(img):
    """A 雅致衬线：混合大小写 + 渐变填充（高雅）"""
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(BODONI_I, 62)
    f2 = ImageFont.truetype(BODONI_I, 62)
    sub = ImageFont.truetype(GARA, 15)
    d.text((392, 96), "Haoyi", font=f1, fill=hx(TITLE), anchor="rm")
    grad_text(img, (400, 96), "Wang", f2, "#7ff0ff", "#3fb6d8", anchor="lm")
    d.line([(300, 122), (600, 122)], fill=hx(LINE) + (110,), width=1)
    d.text((450, 140), "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E",
           font=sub, fill=hx(SUB), anchor="mm")
    chips(d, 168)


def v_b(img):
    """B 大小对比：巨大衬线首名 + 手写姓氏（强烈层级）"""
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(BODONI_I, 74)
    scr = ImageFont.truetype(SCRIPT, 44)
    sub = ImageFont.truetype(GARA, 14)
    d.text((320, 98), "Haoyi", font=big, fill=hx(TITLE), anchor="rm")
    grad_text(img, (330, 100), "Wang", scr, "#8fe6f5", "#3fb6d8", anchor="lm")
    d.line([(300, 124), (620, 124)], fill=hx(LINE) + (95,), width=1)
    d.text((300, 140), "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E",
           font=sub, fill=hx(SUB), anchor="ls")
    chips(d, 170)


def v_c(img):
    """C 手写优雅：Segoe Script（优雅手写）"""
    d = ImageDraw.Draw(img)
    s = ImageFont.truetype(SCRIPT, 66)
    sub = ImageFont.truetype(GARA, 15)
    grad_text(img, (450, 88), "Haoyi Wang", s, "#a8ecff", "#4fc3e8", anchor="mm")
    d.line([(300, 130), (600, 130)], fill=hx(LINE) + (90,), width=1)
    d.text((450, 146), "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E",
           font=sub, fill=hx(SUB), anchor="mm")
    chips(d, 172)


def v_d(img):
    """D 可爱手写：Segoe Print + 手绘下划线 + 小星点（可爱风）"""
    d = ImageDraw.Draw(img)
    p = ImageFont.truetype(PRINT, 54)
    sub = ImageFont.truetype(MSYH, 14)
    d.text((450, 88), "Haoyi", font=p, fill=hx(TITLE), anchor="mm")
    y = 118
    for (x0, x1) in ((330, 430), (436, 520), (526, 600)):
        d.line([(x0, y), (x1, y)], fill=hx("#7ff0ff") + (200,), width=3)
    d.text((450, 146), "地理信息 × 人工智能", font=sub, fill=hx(SUB), anchor="mm")
    for (sx, sy, r) in ((300, 80, 3), (612, 88, 2.4), (286, 140, 2.2)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=hx("#7ff0ff") + (190,))
    chips(d, 170)


def v_e(img):
    """E 首字母大写花体 + 极小副行（杂志封面感·高雅）"""
    d = ImageDraw.Draw(img)
    drop = ImageFont.truetype(BODONI_B, 96)
    rest = ImageFont.truetype(BODONI_I, 52)
    sub = ImageFont.truetype(UI, 12)
    cap = ImageFont.truetype(UI_B, 11)
    d.text((296, 96), "H", font=drop, fill=hx("#7ff0ff"), anchor="rm")
    d.text((308, 104), "aoyi", font=rest, fill=hx(TITLE), anchor="lm")
    d.text((430, 96), "W", font=ImageFont.truetype(BODONI_I, 30), fill=hx(LINE), anchor="rm")
    d.text((440, 98), "ang", font=ImageFont.truetype(BODONI_I, 24), fill=hx(SUB), anchor="lm")
    d.line([(296, 122), (560, 122)], fill=hx(LINE) + (90,), width=1)
    d.text((296, 138), "G E O S P A T I A L   ×   A I   E N G I N E E R I N G",
           font=sub, fill=hx(SUB), anchor="ls")
    d.text((604, 138), "WUHAN", font=cap, fill=hx(CHIP_S), anchor="rs")
    chips(d, 168)


VARIANTS = [("A  雅致衬线 · 渐变 · 混合大小写", v_a),
            ("B  大小对比 · 巨大衬线首名 + 手写姓氏", v_b),
            ("C  手写优雅 · Segoe Script", v_c),
            ("D  可爱手写 · Segoe Print + 手绘线", v_d),
            ("E  杂志封面 · 首字母花体 + 极小副行", v_e)]


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in VARIANTS:
        img = base_canvas()
        fn(img)
        p = os.path.join(OUT, "typo-%s.png" % name[0])
        img.save(p)
        print("wrote %-6s %s" % (name[0], p))

    # 拼成一张对比图
    lab = ImageFont.truetype(MSYH, 15)
    pad, lab_h = 14, 30
    sheet = Image.new("RGB", (W + pad * 2, (H + lab_h) * len(VARIANTS) + pad * (len(VARIANTS) + 1)), (13, 17, 23))
    d = ImageDraw.Draw(sheet)
    y = pad
    for name, fn in VARIANTS:
        d.text((pad, y + 6), name, font=lab, fill=(200, 210, 220))
        sheet.paste(base_canvas() if False else (lambda i: (fn(i), i)[1])(base_canvas()), (pad, y + lab_h))
        y += H + lab_h + pad
    p = os.path.join(OUT, "typography-sheet.png")
    sheet.save(p)
    print("sheet %s" % p)


if __name__ == "__main__":
    main()
