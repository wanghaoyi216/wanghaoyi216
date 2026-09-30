# -*- coding: utf-8 -*-
"""
打字机（GIF）—— 白粉浅底上逐字打出一句话。

为什么背景是浅色而不是透明
------------------------
GIF 只支持 1-bit 透明。做成透明的话，GitHub 浅色模式下没问题，
但访客切到深色模式时，深玫瑰色的字落在深色底上直接看不见。
所以给一个很浅的粉底：两种模式下都是"一张浅色小卡片"，和上面的 banner 同源。

为什么不做渐变
--------------
GIF 只有 256 色。深色底上的渐变勉强能糊过去，**白底上的渐变一定出色带**。
所以这里只用平涂背景，渐变留给 banner（SVG 没有这个问题）。
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = r"C:\Windows\Fonts"
CJK = os.path.join(FDIR, "STXINGKA.TTF")      # 华文行楷
EN = os.path.join(FDIR, "comicbd.ttf")        # Comic Sans Bold

W, H = 1000, 92
FS = 40
TRACK = -1.6
MS_TYPE, MS_HOLD, MS_DEL = 68, 1500, 26

# 文案都对着他实际在做的事写，不要放空话
MSGS = [
    "用 AI 解决科研和教学里那些没人愿意写的活",
    "让每一份汇报稿都能自动过四道质量闸门",
    "把 GIS 和大模型接到同一条流水线上",
    "把散落两年的笔记重新织成能检索的星图",
]

def _fit(draw, text, fs, font_paths):
    """中文走行楷、英文走 Comic Sans，逐字符挑字体。"""
    out = []
    for ch in text:
        f = font_paths[0] if ord(ch) > 0x2000 else font_paths[1]
        out.append((ch, f))
    return out


def build(theme_name, out_path):
    th = T.get(theme_name)
    bg = T.hx(th["bg"][1])
    fg = T.hx(th["typing"])

    f_cjk = ImageFont.truetype(CJK, FS)
    f_en = ImageFont.truetype(EN, FS)
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))

    def w_of(s):
        w = 0.0
        for ch in s:
            f = f_cjk if ord(ch) > 0x2000 else f_en
            w += probe.textlength(ch, font=f) + TRACK
        return w

    frames, durs = [], []
    rainbow = [T.hx(c) for c in T.RAINBOW]
    for mi, msg in enumerate(MSGS):
        full = w_of(msg) + 26
        x0 = int(W / 2 - full / 2)
        # 光标按句轮换彩虹色，和 banner 的彩虹呼应，但只有光标着色 ——
        # 整行字上彩虹会和 banner 抢注意力，而且在 256 色下更容易糊
        caret = rainbow[mi % len(rainbow)]
        # 打字 -> 停顿 -> 逐字删除 -> 留白
        plan = [("type", n) for n in range(1, len(msg) + 1)]
        plan.append(("hold", len(msg)))
        plan += [("del", n) for n in range(len(msg) - 1, 0, -1)]
        plan.append(("gap", 0))

        for kind, n in plan:
            text = msg[:n] if kind != "gap" else ""
            img = Image.new("RGB", (W, H), bg)
            d = ImageDraw.Draw(img)
            x = x0
            for ch in text:
                f = f_cjk if ord(ch) > 0x2000 else f_en
                d.text((x, H / 2), ch, font=f, fill=fg, anchor="lm")
                x += probe.textlength(ch, font=f) + TRACK
            # 光标：竖线 + 呼吸亮度
            a = 0.55 + 0.45 * abs(math.sin(math.pi * (len(frames) % 8) / 8.0))
            d.rectangle([x + 3, H / 2 - FS * 0.46, x + 9, H / 2 + FS * 0.46],
                        fill=caret + (int(255 * a),))
            frames.append(img)
            durs.append({"hold": MS_HOLD, "del": MS_DEL}.get(kind, MS_TYPE))

    # 全部帧共用一套调色板：逐帧 ADAPTIVE 会摧毁跨帧压缩，体积翻几倍
    sample = Image.new("RGB", (W, H * 2))
    for i in range(2):
        sample.paste(frames[i], (0, H * i))
    pal = sample.quantize(colors=64, method=Image.MEDIANCUT)
    pf = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # disposal=1（不清屏）在这里是安全的：每帧都是整张重画的完整图，
    # 删字时那些像素变回背景色，属于"实际发生变化"，会被帧间差分正常记录。
    # 改成 disposal=2 也能正确显示，但每帧都要整块存储，体积从 92KB 涨到 647KB。
    pf[0].save(out_path, save_all=True, append_images=pf[1:],
               duration=durs, loop=0, optimize=True, disposal=1)
    return out_path


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else T.ACTIVE
    out = os.path.join(ROOT, "assets", "themes", name, "typing.gif")
    build(name, out)
    print("  typing %-8s %s  (%.1f KB)" % (name, out, os.path.getsize(out) / 1024))


if __name__ == "__main__":
    main()
