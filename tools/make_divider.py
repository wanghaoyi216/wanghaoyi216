# -*- coding: utf-8 -*-
"""
装饰分隔线（SVG，静态即可）。

用法：在 README 的分区之间插
    <div align="center"><img src="./assets/divider.svg" width="520"></div>

设计和 banner 同源：桃红→橙金的暖色渐变线 + 两端星光，
所以整页是"一个视觉系统"，而不是拼凑。
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

W, H = 520, 34
STOPS = [(0.00, (120, 70, 90)),
         (0.22, (255, 138, 143)),
         (0.50, (255, 226, 180)),
         (0.78, (255, 196, 108)),
         (1.00, (120, 70, 90))]


def build():
    stops = "".join('<stop offset="%.2f" stop-color="#%02X%02X%02X"/>' % (p, c[0], c[1], c[2])
                    for p, c in STOPS)
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="presentation" aria-hidden="true">' % (W, H, W, H)]
    s.append('<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0">%s</linearGradient>'
             '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
             '<stop offset="0%%" stop-color="#FFD9A0" stop-opacity="0.35"/>'
             '<stop offset="100%%" stop-color="#FFD9A0" stop-opacity="0"/>'
             '</radialGradient></defs>' % stops)
    # 中央柔光
    s.append('<ellipse cx="%d" cy="%d" rx="120" ry="12" fill="url(#glow)"/>' % (W // 2, H // 2))
    # 左右渐隐的线
    s.append('<line x1="26" y1="%d" x2="%d" y2="%d" stroke="url(#g)" stroke-width="2" '
             'stroke-linecap="round" opacity="0.9"/>' % (H // 2, W // 2 - 26, W // 2 - 26))
    s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="url(#g)" stroke-width="2" '
             'stroke-linecap="round" opacity="0.9"/>' % (W // 2 + 26, H // 2, W - 26, H // 2))
    # 中央菱形
    cx, cy, r = W // 2, H // 2, 7
    s.append('<path d="M %d %d L %d %d L %d %d L %d %d Z" fill="url(#g)"/>'
             % (cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy))
    s.append('<circle cx="%d" cy="%d" r="2.2" fill="#FFF0D8"/>' % (cx, cy))
    # 两端小星
    for (x, y, rr) in ((26, H // 2, 4.2), (W - 26, H // 2, 4.2)):
        s.append('<path d="M %d %d L %d %d L %d %d L %d %d Z" fill="url(#g)" opacity="0.95"/>'
                 % (x, y - rr, x + rr, y, x, y + rr, x - rr, y))
    # 散落小点
    for (x, y, rr) in ((120, 9, 1.5), (400, 25, 1.7), (200, 25, 1.3), (300, 8, 1.4)):
        s.append('<circle cx="%d" cy="%d" r="%s" fill="#FFCE9B" opacity="0.75"/>' % (x, y, rr))
    s.append("</svg>")
    return "".join(s)


def main():
    p = os.path.join(OUT, "divider.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(build())
    print("wrote %s  (%d bytes)" % (p, os.path.getsize(p)))


if __name__ == "__main__":
    main()
