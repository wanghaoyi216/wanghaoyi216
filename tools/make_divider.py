# -*- coding: utf-8 -*-
"""
装饰分隔线（SVG，静态）。配色来自 tools/theme.py。
用法：<div align="center"><img src="./assets/divider.svg" width="520"></div>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 520, 34


def build(theme_name, out_path):
    th = T.get(theme_name)
    grad = list(th["name_grad"])
    grad[0] = th["chip_text"]
    grad[-1] = th["chip_text"]
    stops = "".join('<stop offset="%.2f" stop-color="#%s"/>' % (p, c.lstrip("#"))
                    for p, c in zip([0.0, 0.22, 0.5, 0.78, 1.0], grad))
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="presentation" aria-hidden="true">' % (W, H, W, H)]
    s.append('<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0">%s</linearGradient>'
             '<radialGradient id="gl" cx="0.5" cy="0.5" r="0.5">'
             '<stop offset="0%%" stop-color="%s" stop-opacity="0.32"/>'
             '<stop offset="100%%" stop-color="%s" stop-opacity="0"/>'
             '</radialGradient></defs>' % (stops, th["star"], th["star"]))
    s.append('<ellipse cx="%d" cy="%d" rx="120" ry="12" fill="url(#gl)"/>' % (W // 2, H // 2))
    for x1, x2 in ((26, W // 2 - 26), (W // 2 + 26, W - 26)):
        s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="url(#g)" stroke-width="2" '
                 'stroke-linecap="round" opacity="0.9"/>' % (x1, H // 2, x2, H // 2))
    cx, cy, r = W // 2, H // 2, 7
    s.append('<path d="M %d %d L %d %d L %d %d L %d %d Z" fill="url(#g)"/>'
             % (cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy))
    s.append('<circle cx="%d" cy="%d" r="2.2" fill="%s"/>' % (cx, cy, th["star"]))
    for x in (26, W - 26):
        s.append('<path d="M %d %d L %d %d L %d %d L %d %d Z" fill="url(#g)" opacity="0.95"/>'
                 % (x, H // 2 - 4, x + 4, H // 2, x, H // 2 + 4, x - 4, H // 2))
    for (x, y, rr) in ((120, 9, 1.5), (400, 25, 1.7), (200, 25, 1.3), (300, 8, 1.4)):
        s.append('<circle cx="%d" cy="%d" r="%s" fill="%s" opacity="0.75"/>' % (x, y, rr, th["star"]))
    s.append("</svg>")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(s))
    return out_path


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else T.ACTIVE
    p = os.path.join(ROOT, "assets", "themes", name, "divider.svg")
    build(name, p)
    print("  divider %-8s %s  (%.1f KB)" % (name, p, os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()
