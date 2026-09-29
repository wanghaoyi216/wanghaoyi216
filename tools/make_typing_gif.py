# -*- coding: utf-8 -*-
"""
把打字机效果做成 GIF。

为什么必须是 GIF 而不是 SVG：
  Chrome 在把 SVG 当作 <img> 渲染时（也就是 GitHub README 的场景）不执行 SMIL 动画。
  实测证据：
    · <textPath> + 动画 d  -> 文字宽度停在 0，空白
    · <clipPath> 内动画 width -> 不生效，空白
    · 普通元素 opacity 轮播 -> 不生效，基准值 opacity=0，全空白
    · 同一张 banner 里的元素因为有"可用的静态基准值"，所以看起来正常（其实是静态的）
  GIF 在 <img> 里一定动，所以打字机改用 GIF 实现。
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

W, H = 760, 82
FS = 24
LINES = [
    "用 AI 解决科研和教学里的麻烦事",
    "Python / Java / Vue 全栈开发",
    "Building tools that actually run",
]

CJK_FONT = r"C:\Windows\Fonts\msyh.ttc"

# 每一行：打字 -> 停留 -> 擦除
TYPE_F, HOLD_F, ERASE_F = 0.58, 0.16, 0.26
LOOP = TYPE_F + HOLD_F + ERASE_F


def font(size):
    return ImageFont.truetype(CJK_FONT, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def build(fname, color):
    f = font(FS)
    rgb = ImageColor.getrgb(color) + (255,)   # "#58A6FF" -> (r,g,b,255)
    probe = Image.new("RGB", (10, 10))
    pd = ImageDraw.Draw(probe)
    widths = [text_w(pd, l, f) for l in LINES]

    frames = []
    steps = 26  # 每行的帧数
    total = steps * len(LINES)

    for idx in range(total):
        i = idx // steps
        k = idx % steps
        phase = k / steps
        line = LINES[i]
        full = widths[i]

        if phase < TYPE_F:
            # 打字：按比例截断字符数
            n = max(1, int(round(len(line) * (phase / TYPE_F))))
            shown = line[:n]
            cur_x = None
        elif phase < TYPE_F + HOLD_F:
            shown = line
            cur_x = None
        else:
            # 擦除：反向截断
            p = (phase - TYPE_F - HOLD_F) / ERASE_F
            n = max(0, int(round(len(line) * (1 - p))))
            shown = line[:n]
            cur_x = None

        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        x = (W - text_w(d, shown, f)) / 2
        y = (H - FS * 1.35) / 2
        d.text((x, y), shown, font=f, fill=rgb)

        # 光标
        if shown:
            cw = text_w(d, shown, f)
            cx = (W - full) / 2 + cw + 3
            cy = (H - FS * 1.35) / 2 + 2
            d.rectangle([cx, cy, cx + 5, cy + FS + 2], fill=rgb)

        # RGBA -> P，并把最后一个调色板索引留给"透明"，
        # 这样 GIF 放在深色或浅色背景上都不会出现黑框。
        alpha = img.split()[3]
        pimg = img.convert("RGB").quantize(colors=255)
        transparent_mask = Image.eval(alpha, lambda a: 255 if a < 128 else 0)
        pimg.paste(255, transparent_mask)
        pimg.info["transparency"] = 255

        frames.append(pimg)

    path = os.path.join(OUT, fname)
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=70,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return path


def main():
    for color, fname in (("#58A6FF", "typing-dark.gif"), ("#0969DA", "typing-light.gif")):
        p = build(fname, color)
        print("wrote %-22s %8.1f KB" % (fname, os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()


