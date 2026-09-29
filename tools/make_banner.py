# -*- coding: utf-8 -*-
"""
banner（SVG，静态）—— 白 → 淡粉底 + 深玫瑰→珊瑚粉渐变名字。
配色来自 tools/theme.py。

为什么改回 SVG 而不是 GIF
-----------------------
之前为了"流动+波浪"动画做成了 GIF，代价是 256 色量化：
在**深色**背景上勉强能看，但在**白色/浅粉**背景上会出现明显的色带（banding），
浅色渐变恰恰是 GIF 最容易崩的场景。现在动画交给打字机 GIF，
banner 回到 SVG：渐变绝对平滑、文件小几倍、文字边缘锐利。

为什么不加动画
-------------
SVG 里的 SMIL 在 GitHub 的 <img> 上下文不执行（实测 textPath/clipPath/opacity
三种方案全变空白）。要动只能 GIF，代价是上面的色带。**为了"干净"放弃"会动"。**

设计克制
--------
之前那版有 46 颗闪烁星光、三层呼吸光晕、两组等高线、一条来回扫的亮条，
反馈是"装饰太密、特别难看"。现在只留：底色渐变 + 三个很淡的色晕、
名字、一条细线、一行副标题、四颗胶囊。深色只出现在**文字**里，不做背景。
"""
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = r"C:\Windows\Fonts"
SERIF_B = os.path.join(FDIR, "BOD_B.TTF")
SCRIPT = os.path.join(FDIR, "segoesc.ttf")
CJK_B = os.path.join(FDIR, "msyhbd.ttc")

W, H = 1000, 260
CHIP_TEXT = ["中国地质大学（武汉）", "地理信息工程 · 硕士在读",
             "Python / Java / Vue", "Wuhan · China"]

# ---------------------------------------------------------------- 字体 -> 路径
_fcache = {}


def _font(path):
    if path not in _fcache:
        f = TTFont(path, fontNumber=0, lazy=True)
        _fcache[path] = (f, f["head"].unitsPerEm, f.getBestCmap(), f["hmtx"], f.getGlyphSet())
    return _fcache[path]


def text_metrics(fontpath, text, size):
    """一行文字 -> SVG path 数据 + 视觉包围盒。

    必须用 BoundsPen 的视觉包围盒而不是 advance width 来做居中：
    斜体/手写体这两类字体的字宽和视觉边界差很多，用字宽居中会明显偏。
    """
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


def emit_path(cmd, bnd, tx, ty, hx="mm", hy="mm", fill="#000", extra=""):
    x0, y0, x1, y1 = bnd
    dx = {"l": -x0, "m": -(x0 + x1) / 2.0, "r": -x1}[hx]
    dy = {"t": -y0, "m": -(y0 + y1) / 2.0, "b": -y1}[hy]
    return ('<path d="%s" transform="translate(%.1f,%.1f)" fill="%s"%s/>'
            % (cmd, tx + dx, ty + dy, fill, extra))


def path_text(fontpath, text, size, tx, ty, hx="mm", hy="mm", fill="#000"):
    cmd, bnd = text_metrics(fontpath, text, size)
    return emit_path(cmd, bnd, tx, ty, hx, hy, fill)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else T.ACTIVE
    out = os.path.join(ROOT, "assets", "themes", name, "banner.svg")
    build(name, out)
    print("  banner %-8s %s  (%.1f KB)" % (name, out, os.path.getsize(out) / 1024))


def build(theme_name, out_path):
    th = T.get(theme_name)
    c = lambda v: v.lstrip("#").upper()

    # 名字渐变的 5 个色标
    ng = th["name_grad"]
    stops = "".join('<stop offset="%.2f" stop-color="%s"/>'
                    % (p, ng[i]) for i, p in enumerate([0, .25, .5, .75, 1]))

    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-label="Haoyi Wang">' % (W, H, W, H)]
    s.append("<defs>")
    s.append('<linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">'
             '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
             % (th["bg"][0], th["bg"][1]))
    s.append('<linearGradient id="ng" x1="0" y1="0" x2="1" y2="0">%s</linearGradient>' % stops)
    s.append('<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="%s" stop-opacity="0"/>'
             '<stop offset="0.5" stop-color="%s"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>'
             % (th["accent"], th["accent"], th["accent"]))
    for i, col in enumerate(th["glows"][:3]):
        s.append('<radialGradient id="g%d" cx="0.5" cy="0.5" r="0.5">'
                 '<stop offset="0%%" stop-color="%s" stop-opacity="0.85"/>'
                 '<stop offset="100%%" stop-color="%s" stop-opacity="0"/></radialGradient>'
                 % (i, col, col))
    s.append("</defs>")

    # 底：白 -> 淡粉（对角线，别做成上下，否则像渐变遮罩）
    s.append('<rect width="%d" height="%d" fill="url(#bg)"/>' % (W, H))
    # 三个很淡的色晕，给白底一点层次。位置刻意不对称，避免"三个一样的圆"那种呆板感
    for i, (cx, cy, rx) in enumerate(((170, 40, 300), (860, 200, 340), (520, 250, 280))):
        s.append('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="url(#g%d)"/>'
                 % (cx, cy, rx, int(rx * 0.62), i))

    # 名字：Haoyi（Bodoni Bold 巨大）+ Wang（Segoe Script 手写）
    f_a, f_b = SERIF_B, SCRIPT
    sa, sb = 92, 54
    w_a, w_b = text_width(f_a, "Haoyi", sa), text_width(f_b, "Wang", sb)
    gap = 10
    x0 = W / 2 - (w_a + gap + w_b) / 2
    s.append(path_text(f_a, "Haoyi", sa, x0 + w_a, 112, "r", "m", "url(#ng)"))
    s.append(path_text(f_b, "Wang", sb, x0 + w_a + gap, 118, "l", "m", "url(#ng)"))

    # 名字下面一条很细的渐变线
    s.append('<line x1="%d" y1="152" x2="%d" y2="152" stroke="url(#rule)" stroke-width="1.6"/>'
             % (int(W / 2 - 300), int(W / 2 + 300)))

    # 副标题
    s.append(path_text(SERIF_B, "G E O S P A T I A L   ×   A R T I F I C I A L   "
                                "I N T E L L I G E N C E", 15, W / 2, 176,
                       "m", "m", th["sub"]))

    # 四颗胶囊
    f_chip = CJK_B
    cw = [int(text_width(f_chip, t, 15)) + 40 for t in CHIP_TEXT]
    total = sum(cw) + 10 * (len(cw) - 1)
    x = int(W / 2 - total / 2)
    for t, w in zip(CHIP_TEXT, cw):
        s.append('<rect x="%d" y="198" width="%d" height="34" rx="17" fill="%s" '
                 'stroke="%s" stroke-width="1.4"/>' % (x, w, th["chips"][0], th["contour"]))
        s.append(path_text(f_chip, t, 15, x + w / 2, 215, "m", "m", th["chip_text"]))
        x += w + 10

    # 底部一条极细的强调线
    s.append('<rect x="0" y="%d" width="%d" height="3" fill="%s" opacity="0.5"/>' % (H - 3, W, th["accent"]))
    s.append("</svg>")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(s))
    return out_path


if __name__ == "__main__":
    main()
