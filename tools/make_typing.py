# -*- coding: utf-8 -*-
"""
自制打字机动画 SVG（v3）。

踩坑记录，直接决定了这一版的实现方式：
  · readme-typing-svg.demolab.com 靠动画 <path> 的 d 配合 <textPath> 擦出文字，
    Chrome 在把 SVG 当 <img> 渲染时（GitHub README 就是这种情形）不驱动它 -> 空白。
  · 我自己的 v2 用 <clipPath><rect> 的 width 动画，单独打开正常，嵌进 GitHub 仍空白。
    原因：<defs>/<clipPath> 里的 SMIL 动画在 SVG-as-image 下不被采样。
    （同页面上的光标 <rect> 是普通元素，opacity/x 动画就正常跑。）
  · v3 方案：不做遮罩、不做裁剪，全部用普通元素的 opacity 动画 ——
    每一行文字铺若干个「逐字变长的副本」，按时序轮播出打字效果。
    只依赖已在 banner 上验证可用的原语，且不依赖任何背景色。
"""
import os
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

W, H = 720, 76
FS = 22
LINES = [
    "用 AI 解决科研和教学里的麻烦事",
    "Python / Java / Vue 全栈开发",
    "Building tools that actually run",
]

TYPE_FRAC = 0.60   # 打字过程占本行时长的比例
HOLD_FRAC = 0.14   # 打完停留
ERASE_FRAC = 0.26  # 擦除过程


def width_estimate(s, fs=FS):
    w = 0.0
    for ch in s:
        if ch == " ":
            w += fs * 0.28
        elif unicodedata.east_asian_width(ch) in ("W", "F"):
            w += fs * 1.0
        else:
            w += fs * 0.56
    return w


def build(color):
    n = len(LINES)
    cycle = TYPE_FRAC + HOLD_FRAC + ERASE_FRAC          # 1.0
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
           'role="img" aria-label="typing">' % (W, H, W, H)]
    out.append(
        '<g font-family="Noto Sans SC, Microsoft YaHei, PingFang SC, Segoe UI, Helvetica, Arial, sans-serif" '
        'font-size="%d" font-weight="600" fill="%s" text-anchor="middle">' % (FS, color)
    )

    for i, line in enumerate(LINES):
        t0 = i * cycle
        t1 = t0 + cycle
        dur = n * cycle
        for k in range(1, len(line) + 1):
            txt = line[:k]
            a = t0 + TYPE_FRAC * (k - 1) / len(line)
            b = t0 + TYPE_FRAC * k / len(line)
            c = t0 + TYPE_FRAC + HOLD_FRAC
            d = t0 + cycle
            begin = a / cycle * dur          # 换算成整个 dur 的时间轴
            out.append(
                '<text x="%d" y="%d" opacity="0">%s'
                '<animate attributeName="opacity" '
                'values="0;0;1;1;0;0" keyTimes="0;%.5f;%.5f;%.5f;%.5f;1" '
                'dur="%ss" begin="%ss" repeatCount="indefinite"/>'
                '</text>' % (W // 2, H // 2 + FS * 0.36, txt,
                             max(0.0, (a) / dur), max(0.0, (b) / dur),
                             max(0.0, (c) / dur), max(0.0, (d) / dur),
                             dur, begin)
            )
    out.append("</g>")
    out.append("</svg>")
    return "".join(out)


def main():
    for color, fname in (("#58A6FF", "typing-dark.svg"), ("#0969DA", "typing-light.svg")):
        p = os.path.join(OUT, fname)
        with open(p, "w", encoding="utf-8") as f:
            f.write(build(color))
        print("wrote %-20s %6d bytes" % (fname, os.path.getsize(p)))


if __name__ == "__main__":
    main()
