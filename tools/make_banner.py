# -*- coding: utf-8 -*-
"""
个人主页 banner 生成器（B 方案：巨大衬线首名 + 手写姓氏）。

关键设计决策
------------
1. 排版改用 Bodoni MT Italic（首名）+ Segoe Script（姓氏），
   替换掉原来「全大写 + 均匀字距 + 无衬线」的板正写法。
   混合大小写本身就是最快去"板正感"的手段。

2. 文字全部转成矢量路径（fontTools SVGPathPen）再嵌进 SVG。
   原因：Bodoni MT / Segoe Script 只在 Windows 上装了，
   如果只写 font-family，Mac / Linux 访客会掉字体、排版直接崩。
   转路径后任何系统渲染完全一致，体积也几乎不增加
   （对比：内嵌字体 base64 要多 800KB，转路径只多几 KB）。

3. 只做深色版。用户反馈浅色版"违反常识、效果很差"——
   浅色 banner 本身发灰、且和下方内容衔接生硬，
   为了凑双主题硬做一套更差的设计才是问题所在。顶级主页普遍是 hero 恒定深色。
"""
import math
import os

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

W, H = 1200, 300
FDIR = r"C:\Windows\Fonts"

SERIF_I = os.path.join(FDIR, "BOD_I.TTF")    # Bodoni MT Italic
SCRIPT = os.path.join(FDIR, "segoesc.ttf")   # Segoe Script
SERIF_R = os.path.join(FDIR, "BOD_R.TTF")    # Bodoni MT
UI = os.path.join(FDIR, "segoeui.ttf")
CJK = os.path.join(FDIR, "msyh.ttc")

BG1, BG2, BG3 = "#04121f", "#0a2333", "#0d3a45"
LINE = "#5fd0e6"
GRID = "#2c6b80"
TITLE = "#eaf7fb"
SUB = "#8fd4e6"
CHIP_BG = "#0f3a4a"
CHIP_S = "#7fc9dc"
ACCENT_HI = "#7ff0ff"
ACCENT_LO = "#3fb6d8"

CHIPS = ["中国地质大学（武汉）", "硕士在读", "地理信息 · AI 工程"]


# --------------------------------------------------------------- 字体 -> 路径
_fcache = {}


def _font(path):
    if path not in _fcache:
        f = TTFont(path, fontNumber=0, lazy=True)
        _fcache[path] = (f, f["head"].unitsPerEm, f.getBestCmap(), f["hmtx"], f.getGlyphSet())
    return _fcache[path]


def text_metrics(fontpath, text, size):
    """把一行文字转成 SVG path，并返回其视觉包围盒。"""
    f, upem, cmap, hmtx, glyphset = _font(fontpath)
    scale = size / upem
    out = SVGPathPen(glyphset, ntos=lambda v: "%.2f" % v)
    bnd = BoundsPen(glyphset)
    x = 0.0
    space = hmtx["space"][0] * scale
    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            x += space
            continue
        t = Transform(scale, 0, 0, -scale, x, 0)   # 字体 Y 向上，SVG Y 向下 -> 取反
        glyphset[gname].draw(TransformPen(out, t))
        glyphset[gname].draw(TransformPen(bnd, t))
        x += hmtx[gname][0] * scale
    return "".join(out.getCommands()), bnd.bounds


def text_width(fontpath, text, size):
    f, upem, cmap, hmtx, _ = _font(fontpath)
    scale = size / upem
    w = 0.0
    for ch in text:
        g = cmap.get(ord(ch))
        w += (hmtx[g][0] if g else hmtx["space"][0]) * scale
    return w


def emit(cmd, bounds, tx, ty, hx="mm", fill=TITLE, opacity=None, extra=""):
    """按锚点把路径摆到 (tx, ty)。hx: l/m/r  vy: t/m/b"""
    x0, y0, x1, y1 = bounds
    dx = {"l": -x0, "m": -(x0 + x1) / 2.0, "r": -x1}[hx[0]]
    dy = {"t": -y0, "m": -(y0 + y1) / 2.0, "b": -y1}[hx[1]]
    op = '' if opacity is None else ' opacity="%.3f"' % opacity
    return ('<path d="%s" transform="translate(%.1f,%.1f)" fill="%s"%s%s/>'
            % (cmd, tx + dx, ty + dy, fill, op, extra))


def draw_text(s, fontpath, text, size, tx, ty, hx="mm", fill=TITLE, opacity=None, gradient=None):
    cmd, bnd = text_metrics(fontpath, text, size)
    if gradient:
        gx0 = tx - (bnd[2] - bnd[0]) / 2.0
        gid = "tg%d" % len(s)
        s.append(
            '<linearGradient id="%s" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%%" stop-color="%s"/><stop offset="100%%" stop-color="%s"/>'
            '</linearGradient>' % (gid, gradient[0], gradient[1]))
        fill = "url(#%s)" % gid
    s.append(emit(cmd, bnd, tx, ty, hx, fill, opacity))


def draw_spaced(s, fontpath, text, size, tracking, tx, ty, fill=SUB):
    """手动字距（SVG 的 letter-spacing 对中文/字距需求不好控）。"""
    total = text_width(fontpath, text, size) + tracking * max(0, len(text) - 1)
    x = tx - total / 2.0
    for ch in text:
        if ch == " ":
            x += text_width(fontpath, " ", size) + tracking
            continue
        cmd, bnd = text_metrics(fontpath, ch, size)
        s.append(emit(cmd, bnd, x, ty, "lm", fill))
        x += text_width(fontpath, ch, size) + tracking


# --------------------------------------------------------------- 背景元素
def topo_paths(cx, cy, base_r, seed, rings=9, wobble=(0.16, 0.09, 0.05)):
    paths = []
    for k in range(rings):
        r0 = base_r * (1 + 0.30 * k / max(rings - 1, 1))
        pts = []
        for i in range(241):
            t = 2 * math.pi * i / 240.0
            r = r0
            r *= 1 + wobble[0] * math.sin(3 * t + seed * 0.7)
            r *= 1 + wobble[1] * math.sin(5 * t + seed * 1.9)
            r *= 1 + wobble[2] * math.sin(8 * t + seed * 2.7)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t) * 0.62))
        d = "M %.1f %.1f " % pts[0]
        for (x, y) in pts[1:]:
            d += "L %.1f %.1f " % (x, y)
        paths.append((d + "Z", 1 - 0.055 * k))
    return paths


def build():
    s = []
    s.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
             'role="img" aria-label="Haoyi Wang - Geospatial and AI">' % (W, H, W, H))
    s.append("<defs>")
    s.append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0%%" stop-color="%s"/><stop offset="52%%" stop-color="%s"/>'
             '<stop offset="100%%" stop-color="%s"/></linearGradient>' % (BG1, BG2, BG3))
    s.append('<radialGradient id="g1" cx="18%%" cy="22%%" r="62%%">'
             '<stop offset="0%%" stop-color="#0e7ea8" stop-opacity="0.55"/>'
             '<stop offset="100%%" stop-color="#0a2333" stop-opacity="0"/></radialGradient>')
    s.append('<radialGradient id="g2" cx="84%%" cy="82%%" r="55%%">'
             '<stop offset="0%%" stop-color="#12a594" stop-opacity="0.45"/>'
             '<stop offset="100%%" stop-color="#0a2333" stop-opacity="0"/></radialGradient>')
    s.append('<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0%%" stop-color="%s" stop-opacity="0.85"/>'
             '<stop offset="26%%" stop-color="%s" stop-opacity="0"/>'
             '<stop offset="74%%" stop-color="%s" stop-opacity="0"/>'
             '<stop offset="100%%" stop-color="%s" stop-opacity="0.85"/></linearGradient>' % (BG1, BG1, BG1, BG1))
    s.append('<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0%%" stop-color="#0e7ea8"/><stop offset="50%%" stop-color="#12a594"/>'
             '<stop offset="100%%" stop-color="#0e7ea8"/></linearGradient>')
    s.append('<filter id="soft" x="-30%%" y="-30%%" width="160%%" height="160%%">'
             '<feGaussianBlur stdDeviation="18"/></filter>')
    s.append("</defs>")

    s.append('<rect width="%d" height="%d" fill="url(#bg)"/>' % (W, H))
    s.append('<rect width="%d" height="%d" fill="url(#g1)"/>' % (W, H))
    s.append('<rect width="%d" height="%d" fill="url(#g2)"/>' % (W, H))

    # 地图网格
    s.append('<g stroke="%s" stroke-width="0.6" opacity="0.20">' % GRID)
    for x in range(0, W + 1, 40):
        s.append('<line x1="%d" y1="0" x2="%d" y2="%d"/>' % (x, x, H))
    for y in range(0, H + 1, 30):
        s.append('<line x1="0" y1="%d" x2="%d" y2="%d"/>' % (y, W, y))
    s.append("</g>")

    # 等高线（两组反向旋转 + 中央背光）
    s.append('<g fill="none" stroke="%s" stroke-width="1.1" stroke-linecap="round">' % LINE)
    s.append('<animateTransform attributeName="transform" type="rotate" '
             'from="0 600 150" to="360 600 150" dur="180s" repeatCount="indefinite"/>')
    for d, op in topo_paths(300, 150, 120, 1.0, 8):
        s.append('<path d="%s" opacity="%.3f"/>' % (d, op * 0.75))
    s.append("</g>")

    s.append('<g fill="none" stroke="%s" stroke-width="1.0" stroke-linecap="round" '
             'stroke-dasharray="3 7">' % LINE)
    s.append('<animateTransform attributeName="transform" type="rotate" '
             'from="360 900 150" to="0 900 150" dur="220s" repeatCount="indefinite"/>')
    for d, op in topo_paths(920, 150, 110, 2.3, 7):
        s.append('<path d="%s" opacity="%.3f"/>' % (d, op * 0.55))
    s.append("</g>")

    s.append('<g fill="none" stroke="%s" stroke-width="0.9" opacity="0.30">' % LINE)
    s.append('<animate attributeName="opacity" values="0.18;0.34;0.18" dur="9s" repeatCount="indefinite"/>')
    for d, op in topo_paths(600, 150, 165, 3.7, 6):
        s.append('<path d="%s"/>' % d)
    s.append("</g>")

    # 漂浮光点
    dots = [(150, 240, 2.2, 9.0), (250, 90, 1.6, 11.0), (395, 215, 2.6, 10.0),
            (830, 95, 1.9, 9.5), (1010, 205, 2.4, 12.0), (1120, 110, 1.5, 10.5),
            (470, 60, 1.7, 11.5), (700, 250, 2.0, 9.2), (123, 150, 1.4, 12.5),
            (1075, 150, 1.8, 10.8)]
    s.append('<g fill="%s">' % LINE)
    for (x, y, r, dur) in dots:
        s.append('<circle cx="%d" cy="%d" r="%s" opacity="0.15">'
                 '<animate attributeName="opacity" values="0.05;0.55;0.05" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
                 '<animateTransform attributeName="transform" type="translate" '
                 'values="0 0; 0 -22; 0 0" dur="%ss" begin="%ss" repeatCount="indefinite"/></circle>'
                 % (x, y, r, dur, (x % 7) * 0.4, dur * 1.6, (x % 5) * 0.3))
    s.append("</g>")

    s.append('<rect width="%d" height="%d" fill="url(#fade)"/>' % (W, H))
    s.append('<ellipse cx="600" cy="150" rx="450" ry="122" fill="%s" opacity="0.5" filter="url(#soft)"/>' % BG1)

    # ---------------- 名字：B 方案 ----------------
    # 巨大衬线首名 + 手写姓氏，整块居中（名字/分隔线/副标题/标签共用一条中轴）
    name_size, scr_size = 92, 52
    gap_n = 10
    w_haoyi = text_width(SERIF_I, "Haoyi", name_size)
    w_wang = text_width(SCRIPT, "Wang", scr_size)
    block_l = 600 - (w_haoyi + gap_n + w_wang) / 2.0

    # 首名右对齐到 block_l，手写姓氏左对齐接上，垂直错落 6px
    draw_text(s, SERIF_I, "Haoyi", name_size, block_l + w_haoyi, 128, hx="rm", fill=TITLE)
    draw_text(s, SCRIPT, "Wang", scr_size, block_l + w_haoyi + gap_n, 134, hx="lm",
              gradient=(ACCENT_HI, ACCENT_LO))

    # 细分隔线（比名字块略宽，视觉上收住构图）
    rule_w = max(w_haoyi + w_wang, 470) + 60
    s.append('<line x1="%.1f" y1="168" x2="%.1f" y2="168" stroke="%s" stroke-width="1" opacity="0.32"/>'
             % (600 - rule_w / 2.0, 600 + rule_w / 2.0, LINE))
    # 副标题（手动字距，居中）
    draw_spaced(s, SERIF_R, "GEOSPATIAL  ×  ARTIFICIAL  INTELLIGENCE", 17, 3.4, 600, 196, SUB)

    # 标签胶囊
    fs = 13.0
    widths = [int(text_width(CJK, t, fs) + 36) for t in CHIPS]
    gap = 12
    total = sum(widths) + gap * (len(widths) - 1)
    x = 600 - total / 2.0
    for t, w in zip(CHIPS, widths):
        s.append('<rect x="%.1f" y="214" width="%d" height="29" rx="14.5" fill="%s" '
                 'fill-opacity="0.9" stroke="%s" stroke-opacity="0.5"/>' % (x, w, CHIP_BG, CHIP_S))
        cmd, bnd = text_metrics(CJK, t, fs)
        s.append(emit(cmd, bnd, x + w / 2.0, 228.5, "mm", CHIP_S))
        x += w + gap

    # 底部强调线 + 流光
    s.append('<rect x="0" y="288" width="%d" height="2" fill="url(#accent)" opacity="0.85"/>' % W)
    s.append('<rect x="-260" y="287" width="260" height="4" fill="%s" opacity="0.9">'
             '<animate attributeName="x" values="-260;%d" dur="7s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;0.9;0" dur="7s" repeatCount="indefinite"/>'
             '</rect>' % (ACCENT_HI, W + 20))

    s.append("</svg>")
    return "".join(s)


def main():
    p = os.path.join(OUT, "banner-dark.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(build())
    print("wrote %s  (%d bytes)" % (p, os.path.getsize(p)))


if __name__ == "__main__":
    main()
