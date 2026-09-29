# -*- coding: utf-8 -*-
"""
把 assets/tech/*.svg（simple-icons）合成为几行统一风格的技术栈图标 SVG。

为什么不用 skillicons.dev：
  1. 它在部分网络环境下不稳定（实测多次 0 字节超时）；
  2. 它固定用深色主题，在浅色背景上会突兀；
  3. 自建后图标存在自己的仓库里，永不失效，还能自己控制配色与间距。
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 仓库根目录
TECH = os.path.join(BASE, "assets", "tech")
OUT = os.path.join(BASE, "assets")

ICON = 40          # 图标边长
GAP = 20           # 图标间距
PAD = 4

ROWS = {
    "tech-languages.svg": [
        ("python", "#3776AB", "Python"),
        ("openjdk", "#F89820", "Java"),
        ("typescript", "#3178C6", "TypeScript"),
        ("javascript", "#F7DF1E", "JavaScript"),
        ("html5", "#E34F26", "HTML5"),
        ("css", "#1572B6", "CSS3"),
    ],
    "tech-frameworks.svg": [
        ("vuedotjs", "#42B883", "Vue.js"),
        ("spring", "#6DB33F", "Spring"),
        ("react", "#61DAFB", "React"),
        ("docker", "#2496ED", "Docker"),
        ("git", "#F05032", "Git"),
        ("github", "#8B949E", "GitHub"),   # 中性灰：深浅两种背景都看得见
    ],
    "tech-data.svg": [
        ("mysql", "#4479A1", "MySQL"),
        ("postgresql", "#4169E1", "PostgreSQL"),
        ("redis", "#DC382D", "Redis"),
        ("mongodb", "#47A248", "MongoDB"),
        ("apachekafka", "#231F20", "Kafka"),
        ("nginx", "#009639", "NGINX"),
        ("linux", "#FCC624", "Linux"),
    ],
}


def load(slug):
    p = os.path.join(TECH, slug + ".svg")
    if not os.path.exists(p):
        return None
    s = open(p, encoding="utf-8").read()
    m = re.search(r"<path[^>]*\sd=\"([^\"]+)\"", s)
    if not m:
        m = re.search(r"<path[^>]*d=\"([^\"]+)\"", s)
    if not m:
        return None
    return m.group(1)


def build(fname, items):
    got = []
    for slug, color, label in items:
        d = load(slug)
        if d:
            got.append((d, color, label))
    if not got:
        return None
    n = len(got)
    w = PAD * 2 + n * ICON + (n - 1) * GAP
    h = ICON + PAD * 2
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
           'role="img" aria-label="tech stack">' % (w, h, w, h)]
    for i, (d, color, label) in enumerate(got):
        x = PAD + i * (ICON + GAP)
        out.append('<g transform="translate(%d,%d) scale(%s)">' % (x, PAD, ICON / 24.0))
        out.append('<title>%s</title>' % label)
        out.append('<path d="%s" fill="%s"/>' % (d, color))
        out.append("</g>")
    out.append("</svg>")
    return "".join(out)


def main():
    for fname, items in ROWS.items():
        svg = build(fname, items)
        if svg is None:
            print("!! %s 生成失败（图标文件缺失）" % fname)
            continue
        p = os.path.join(OUT, fname)
        with open(p, "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote %-24s %5d bytes" % (fname, os.path.getsize(p)))


if __name__ == "__main__":
    main()
