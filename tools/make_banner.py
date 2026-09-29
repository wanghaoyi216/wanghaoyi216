# -*- coding: utf-8 -*-
"""
生成个人主页的动态 SVG banner。
主题：等高线（topographic contours）—— 对应地理信息专业背景，不是纯装饰。
动画：SMIL（<animate> / <animateTransform>）。GitHub 以 <img> 渲染 SVG 时会禁用脚本，
      但 SMIL 动画仍然可以播放，因此这个文件既安全又能动。
"""
import math
import os

W, H = 1200, 300
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 仓库根目录
OUT_DIR = os.path.join(ROOT, "assets")


def topo_paths(cx, cy, base_r, seed, rings=9, wobble=(0.16, 0.09, 0.05)):
    """生成一组嵌套的等高线闭合曲线。r(θ) 用多谐波扰动，得到自然的山脊感。"""
    paths = []
    for k in range(rings):
        r0 = base_r * (1 + 0.30 * k / max(rings - 1, 1))
        pts = []
        for i in range(241):  # 240 段足够平滑
            t = 2 * math.pi * i / 240.0
            r = r0
            r *= 1 + wobble[0] * math.sin(3 * t + seed * 0.7)
            r *= 1 + wobble[1] * math.sin(5 * t + seed * 1.9)
            r *= 1 + wobble[2] * math.sin(8 * t + seed * 2.7)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t) * 0.62))
        d = "M %.1f %.1f " % pts[0]
        for (x, y) in pts[1:]:
            d += "L %.1f %.1f " % (x, y)
        d += "Z"
        paths.append((d, 1 - 0.055 * k))
    return paths


def build(dark=True):
    if dark:
        bg1, bg2, bg3 = "#04121f", "#0a2333", "#0d3a45"
        g1a, g1b = "#0e7ea8", "#0a2333"
        g2a, g2b = "#12a594", "#0a2333"
        line = "#5fd0e6"
        grid = "#2c6b80"
        title = "#eaf7fb"
        sub = "#8fd4e6"
        chip = "#0f3a4a"
        chip_s = "#7fc9dc"
    else:
        bg1, bg2, bg3 = "#f2fafd", "#e3f2f8", "#d3e9f2"
        g1a, g1b = "#9fdcf0", "#e3f2f8"
        g2a, g2b = "#a8e6da", "#e3f2f8"
        line = "#2b7f9c"
        grid = "#a9cede"
        title = "#0b2b3a"
        sub = "#1d6d87"
        chip = "#ffffff"
        chip_s = "#1d6d87"

    s = []
    s.append(
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
        'aria-label="Haoyi Wang - Geospatial and AI">' % (W, H, W, H)
    )
    s.append("<defs>")
    s.append(
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0%%" stop-color="%s"/><stop offset="52%%" stop-color="%s"/>'
        '<stop offset="100%%" stop-color="%s"/></linearGradient>' % (bg1, bg2, bg3)
    )
    s.append(
        '<radialGradient id="g1" cx="18%%" cy="22%%" r="62%%">'
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.55"/>'
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/></radialGradient>' % (g1a, g1b)
    )
    s.append(
        '<radialGradient id="g2" cx="84%%" cy="82%%" r="55%%">'
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.45"/>'
        '<stop offset="100%%" stop-color="%s" stop-opacity="0"/></radialGradient>' % (g2a, g2b)
    )
    # 顶部/底部渐隐，让 banner 与页面背景自然衔接
    s.append(
        '<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%%" stop-color="%s" stop-opacity="0.85"/>'
        '<stop offset="26%%" stop-color="%s" stop-opacity="0"/>'
        '<stop offset="74%%" stop-color="%s" stop-opacity="0"/>'
        '<stop offset="100%%" stop-color="%s" stop-opacity="0.85"/></linearGradient>' % (bg1, bg1, bg1, bg1)
    )
    s.append(
        '<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0%%" stop-color="#0e7ea8"/><stop offset="50%%" stop-color="#12a594"/>'
        '<stop offset="100%%" stop-color="#0e7ea8"/></linearGradient>'
    )
    s.append(
        '<filter id="soft" x="-30%%" y="-30%%" width="160%%" height="160%%">'
        '<feGaussianBlur stdDeviation="18"/></filter>'
    )
    s.append("</defs>")

    # ---- 背景 ----
    s.append('<rect width="%d" height="%d" fill="url(#bg)"/>' % (W, H))
    s.append('<rect width="%d" height="%d" fill="url(#g1)"/>' % (W, H))
    s.append('<rect width="%d" height="%d" fill="url(#g2)"/>' % (W, H))

    # ---- 地图网格 ----
    s.append('<g stroke="%s" stroke-width="0.6" opacity="0.20">' % grid)
    for x in range(0, W + 1, 40):
        s.append('<line x1="%d" y1="0" x2="%d" y2="%d"/>' % (x, x, H))
    for y in range(0, H + 1, 30):
        s.append('<line x1="0" y1="%d" x2="%d" y2="%d"/>' % (y, W, y))
    s.append("</g>")

    # ---- 等高线（两组，缓慢反向旋转）----
    s.append('<g fill="none" stroke="%s" stroke-width="1.1" stroke-linecap="round">' % line)
    s.append('<animateTransform attributeName="transform" type="rotate" '
             'from="0 600 150" to="360 600 150" dur="180s" repeatCount="indefinite"/>')
    for d, op in topo_paths(300, 150, 120, seed=1.0, rings=8):
        s.append('<path d="%s" opacity="%.3f"/>' % (d, op * 0.75))
    s.append("</g>")

    s.append('<g fill="none" stroke="%s" stroke-width="1.0" stroke-linecap="round" '
             'stroke-dasharray="3 7">' % line)
    s.append('<animateTransform attributeName="transform" type="rotate" '
             'from="360 900 150" to="0 900 150" dur="220s" repeatCount="indefinite"/>')
    for d, op in topo_paths(920, 150, 110, seed=2.3, rings=7):
        s.append('<path d="%s" opacity="%.3f"/>' % (d, op * 0.55))
    s.append("</g>")

    # 中央等高线（正对标题，做背光）
    s.append('<g fill="none" stroke="%s" stroke-width="0.9" opacity="0.30">' % line)
    s.append('<animate attributeName="opacity" values="0.18;0.34;0.18" '
             'dur="9s" repeatCount="indefinite"/>')
    for d, op in topo_paths(600, 150, 165, seed=3.7, rings=6):
        s.append('<path d="%s"/>' % d)
    s.append("</g>")

    # ---- 漂浮光点 ----
    dots = [(150, 240, 2.2, 9.0), (250, 90, 1.6, 11.0), (395, 215, 2.6, 10.0),
            (830, 95, 1.9, 9.5), (1010, 205, 2.4, 12.0), (1120, 110, 1.5, 10.5),
            (470, 60, 1.7, 11.5), (700, 250, 2.0, 9.2), (123, 150, 1.4, 12.5),
            (1075, 150, 1.8, 10.8)]
    s.append('<g fill="%s">' % line)
    for (x, y, r, dur) in dots:
        s.append(
            '<circle cx="%d" cy="%d" r="%s" opacity="0.15">'
            '<animate attributeName="opacity" values="0.05;0.55;0.05" dur="%ss" '
            'begin="%ss" repeatCount="indefinite"/>'
            '<animateTransform attributeName="transform" type="translate" '
            'values="0 0; 0 -22; 0 0" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '</circle>' % (x, y, r, dur, (x % 7) * 0.4, dur * 1.6, (x % 5) * 0.3)
        )
    s.append("</g>")

    # ---- 底部渐隐 ----
    s.append('<rect width="%d" height="%d" fill="url(#fade)"/>' % (W, H))

    # ---- 文字背光：让标题从等高线里"浮"出来 ----
    s.append('<ellipse cx="600" cy="150" rx="430" ry="118" fill="%s" opacity="0.55" filter="url(#soft)"/>' % bg1)

    # ---- 文字 ----
    font = "Segoe UI, Helvetica Neue, Helvetica, Arial, Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif"
    s.append(
        '<text x="600" y="126" text-anchor="middle" font-family="%s" font-size="52" '
        'font-weight="700" letter-spacing="7" fill="%s">HAOYI WANG</text>' % (font, title)
    )
    s.append(
        '<text x="600" y="162" text-anchor="middle" font-family="%s" font-size="16" '
        'font-weight="500" letter-spacing="4.5" fill="%s">GEOSPATIAL  &#215;  ARTIFICIAL  INTELLIGENCE</text>'
        % (font, sub)
    )

    # ---- 标签组：中文标签既更有信息量，宽度也比英文短得多 ----
    # 宽度按字符实际占位估算：CJK 约 1em，ASCII 约 0.55em
    labels = ["中国地质大学（武汉）", "硕士在读", "地理信息 · AI 工程"]
    fs = 13.0
    ls = 1.2
    gap = 12

    def text_w(t):
        w = 0.0
        for ch in t:
            w += fs * (1.0 if ord(ch) > 0x2E80 else 0.55)
        return w + ls * len(t)

    widths = [int(text_w(t) + 34) for t in labels]
    total = sum(widths) + gap * (len(labels) - 1)
    x = 600 - total / 2.0
    s.append('<g font-family="%s" font-size="%s" letter-spacing="%s" fill="%s">'
             % (font, fs, ls, chip_s))
    for txt, w in zip(labels, widths):
        s.append('<rect x="%.1f" y="196" width="%d" height="28" rx="14" fill="%s" '
                 'fill-opacity="0.9" stroke="%s" stroke-opacity="0.5"/>' % (x, w, chip, chip_s))
        s.append('<text x="%.1f" y="215" text-anchor="middle">%s</text>' % (x + w / 2.0, txt))
        x += w + gap
    s.append("</g>")

    # ---- 底部强调线（带流光）----
    s.append('<rect x="0" y="288" width="%d" height="2" fill="url(#accent)" opacity="0.75"/>' % W)
    s.append(
        '<rect x="-260" y="287" width="260" height="4" fill="#7ff0ff" opacity="0.9">'
        '<animate attributeName="x" values="-260;%d" dur="7s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;0.9;0" dur="7s" repeatCount="indefinite"/>'
        '</rect>' % (W + 20)
    )

    s.append("</svg>")
    return "".join(s)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for dark, fname in ((True, "banner-dark.svg"), (False, "banner-light.svg")):
        p = os.path.join(OUT_DIR, fname)
        with open(p, "w", encoding="utf-8") as f:
            f.write(build(dark))
        print("wrote %s  (%d bytes)" % (p, os.path.getsize(p)))


if __name__ == "__main__":
    main()
