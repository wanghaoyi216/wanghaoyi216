# -*- coding: utf-8 -*-
"""
自制打字机动画 SVG。

为什么不用 readme-typing-svg.demolab.com：
  它靠动画 <path> 的 d 属性配合 <textPath> 来"擦出"文字。
  Chrome 在把 SVG 当作 <img> 渲染时（也就是 GitHub README 里的情形）
  不驱动这种 textPath 动画，于是文字宽度停在 0 -> 整块空白。
  （实测：同一张 SVG 单独打开正常显示，嵌进 GitHub 主页就是空白。）

改用 <clipPath><rect> 的 width 动画，这是普通属性动画，
和 banner 里已验证可用的 <animate attributeName="x"> 同一类原语。
"""
import os
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

W, H = 720, 74
FS = 22
LINES = [
    "用 AI 解决科研和教学里的麻烦事",
    "Python / Java / Vue 全栈开发",
    "Building tools that actually run",
]
STEP = 4.6  # 每行的总时长（秒）


def width_estimate(s, fs=FS):
    """估算文本渲染宽度：CJK 约 1em，拉丁约 0.55em，空格约 0.28em。"""
    w = 0.0
    for ch in s:
        if ch == " ":
            w += fs * 0.28
        elif unicodedata.east_asian_width(ch) in ("W", "F"):
            w += fs * 1.0
        else:
            w += fs * 0.56
    return w


def build(color, cursor=True):
    lens = [width_estimate(l) for l in LINES]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
           'role="img" aria-label="typing">' % (W, H, W, H)]
    out.append("<defs>")
    for i, lw in enumerate(lens):
        out.append(
            '<clipPath id="k%d">'
            '<rect x="0" y="0" width="0" height="%d">'
            '<animate attributeName="width" '
            'values="0;%.0f;%.0f;0" keyTimes="0;0.72;0.9;1" dur="%ss" '
            'begin="%ss" repeatCount="indefinite"/>'
            '</rect></clipPath>' % (i, H, lw * 1.02, lw * 1.02, STEP, i * STEP)
        )
    out.append("</defs>")

    for i, line in enumerate(LINES):
        out.append('<g clip-path="url(#k%d)">' % i)
        out.append(
            '<text x="%d" y="%d" text-anchor="middle" '
            'font-family="Noto Sans SC, Microsoft YaHei, PingFang SC, Segoe UI, Helvetica, Arial, sans-serif" '
            'font-size="%d" font-weight="600" fill="%s">%s</text>'
            % (W // 2, H // 2 + FS * 0.36, FS, color, line)
        )
        out.append("</g>")

    # 光标：跟着每一行一起出现/消失
    for i, lw in enumerate(lens):
        x = (W - lw) / 2.0
        out.append(
            '<rect x="%.1f" y="%d" width="2.5" height="%d" fill="%s" opacity="0">'
            '<animate attributeName="x" values="%.1f;%.1f" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '<animate attributeName="opacity" '
            'values="0;0;0.9;0.9;0;0" keyTimes="0;0.04;0.12;0.82;0.9;1" dur="%ss" '
            'begin="%ss" repeatCount="indefinite"/>'
            '</rect>' % (x, H // 2 - FS * 0.6, FS + 6, color, x, x + lw * 1.02,
                         STEP, i * STEP, STEP, i * STEP)
        )
    out.append("</svg>")
    return "".join(out)


def main():
    for color, fname in (("#58A6FF", "typing-dark.svg"), ("#0969DA", "typing-light.svg")):
        p = os.path.join(OUT, fname)
        with open(p, "w", encoding="utf-8") as f:
            f.write(build(color))
        print("wrote %-20s %5d bytes" % (fname, os.path.getsize(p)))
    for l, lw in zip(LINES, [width_estimate(x) for x in LINES]):
        print("   估算宽度 %6.0f px  <- %s" % (lw, l))


if __name__ == "__main__":
    main()
