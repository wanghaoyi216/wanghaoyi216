# -*- coding: utf-8 -*-
"""
打字机动画（GIF）。

为什么要逐字符选字体
--------------------
banner 的排版语言是「西文衬线 + 中文细体」混搭。
如果打字机统一用一套字体，两者的气质就会打架——这是上一版遗留的
最主要的不一致：banner 已经是艺术排版，打字机却还是黑体。

所以这里按字符选：
  · CJK      -> 微软雅黑 Light（msyhl.ttc，细体，不与 banner 抢视觉）
  · 拉丁/数字 -> Bodoni MT（呼应 banner 里的衬线）

为什么必须是 GIF 而不是 SVG
--------------------------
Chrome 在把 SVG 当 <img> 渲染时（GitHub README 场景）不执行 SMIL 动画，
实测三种方案（textPath 动画 d / clipPath width / opacity 轮播）全部变空白。
GIF 在 <img> 里一定动。
"""
import os
import unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

W, H = 780, 84
FS = 25
FDIR = r"C:\Windows\Fonts"
CJK_LIGHT = os.path.join(FDIR, "msyhl.ttc")   # 微软雅黑 Light
LATIN = os.path.join(FDIR, "BOD_R.TTF")       # Bodoni MT

LINES = [
    "用 AI 解决科研和教学里的麻烦事",
    "Python / Java / Vue 全栈开发",
    "Building tools that actually run",
]

TYPE_F, HOLD_F, ERASE_F = 0.58, 0.16, 0.26

_fc = {}


def is_cjk(ch):
    return unicodedata.east_asian_width(ch) in ("W", "F")


def face(ch, size):
    key = (is_cjk(ch), size)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(CJK_LIGHT if key[0] else LATIN, size)
    return _fc[key]


def draw_line(d, text, cx, cy, color):
    """按字符分别选字体绘制，返回整行宽度。"""
    widths = [d.textlength(ch, font=face(ch, FS)) for ch in text]
    total = sum(widths)
    x = cx - total / 2.0
    for ch, w in zip(text, widths):
        if ch != " ":
            d.text((x, cy), ch, font=face(ch, FS), fill=color)
        x += w
    return total


def line_width(d, text):
    return sum(d.textlength(ch, font=face(ch, FS)) for ch in text)


def build(fname, color):
    rgb = ImageColor.getrgb(color) + (255,)
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    steps = 26
    total = steps * len(LINES)
    frames = []

    for idx in range(total):
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
        full_w = line_width(probe, line)
        shown_w = draw_line(d, shown, W // 2, cy, rgb)

        if shown:
            cx = (W + shown_w) / 2 + 4
            d.rectangle([cx, cy + 2, cx + 2.5, cy + FS + 4], fill=rgb)

        alpha = img.split()[3]
        pimg = img.convert("RGB").quantize(colors=255)
        pimg.paste(255, Image.eval(alpha, lambda a: 255 if a < 128 else 0))
        pimg.info["transparency"] = 255
        frames.append(pimg)

    p = os.path.join(OUT, fname)
    frames[0].save(p, save_all=True, append_images=frames[1:],
                   duration=70, loop=0, optimize=True, disposal=2)
    return p


def main():
    # 只做深色版：浅色版已因"违反常识 + 效果差"被删除
    p = build("typing-dark.gif", "#7fd4ec")
    print("wrote %-22s %8.1f KB" % ("typing-dark.gif", os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()
