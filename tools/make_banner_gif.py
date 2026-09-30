# -*- coding: utf-8 -*-
"""
banner（GIF，会动）—— 白底 + 淡彩光晕 + 彩虹流动的名字。

动的地方只有两处，都很克制：
  1. 名字的填充沿横向缓慢流动（完整光谱一整圈）
  2. 底部一条同样在流动的彩虹细线
背景光晕是静态的 —— 整块画面都在动会让人眼花，而且帧间差分压不住体积。

为什么用 numpy 建渐变
-------------------
1000x290 每帧逐像素填 29 万个点、24 帧就是 700 万次 Python 循环，慢到不可用。
先用 numpy 算出 (H, W, 3) 再转成 Image，是几十毫秒的事。

为什么不把背景也做成动的
----------------------
GIF 只支持 256 色。每帧独立量化会摧毁跨帧压缩，体积直接翻几倍。
背景固定 → 只有名字和细线在变，帧间差分能吃掉绝大部分画面。

彩虹在 256 色下会不会出色带？不会。色带是低彩度窄范围渐变（白→粉）的问题；
彩虹色相跨度大，色相本身就是调色板里最省的部分。实测 24 帧无可见色带、无接缝。
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = r"C:\Windows\Fonts"
SERIF_B = os.path.join(FDIR, "BOD_B.TTF")
SCRIPT = os.path.join(FDIR, "segoesc.ttf")
CJK_B = os.path.join(FDIR, "msyhbd.ttc")

W, H = 1000, 340
FRAMES = 18
MS_FRAME = 105

ART = os.path.join(ROOT, "assets", "art", "cartoon.jpg")

FS_A, FS_B = 96, 56           # 首名 / 姓氏字号
FS_CHIP, FS_SUB = 15, 15

# 胶囊文案（与主题无关）。只放三颗：第四颗「Wuhan · China」既和 GitHub 侧栏
# 的地点栏重复，又正好压在右边山丘那只小吉祥物上。少一颗，构图立刻干净。
CHIP_TEXT = ["中国地质大学（武汉）", "地理信息工程 · 硕士在读",
             "Python / Java / Vue"]


def _base(theme_name):
    """静态底：卡通插画 + 主题色调。每帧共用，只算一次。

    插画是自带版权的生成素材（见 tools/make_art.py），不含任何机构标识。
    找不到时退回程序化的淡彩光晕，页面不至于开天窗。
    """
    th = T.get(theme_name)
    if not os.path.exists(ART):
        img = Image.new("RGB", (W, H), th["bg"][0])
        d = ImageDraw.Draw(img, "RGBA")
        for col, (cx, cy, r) in zip(th["wash"], ((190, 30, 330), (840, 250, 350), (540, 150, 300))):
            d.ellipse([cx - r, cy - int(r * 0.66), cx + r, cy + int(r * 0.66)],
                      fill=T.hx(col) + (215,))
        return img.filter(ImageFilter.GaussianBlur(32))

    art = Image.open(ART).convert("RGB").resize((W, H), Image.LANCZOS)
    # 每套主题往自己的底色上靠一点：同一张插画，六种感觉。
    # 15%/6% 时差异太微妙几乎看不出，20%/9% 刚好能分辨又不至于把插画本身的
    # 彩虹弧和等高线细节吃掉。
    art = Image.blend(art, Image.new("RGB", (W, H), th["bg"][1]), 0.20)
    art = Image.blend(art, Image.new("RGB", (W, H), th["wash"][0]), 0.09)
    return art


def _grad_row(lut, xs, period, off):
    arr = np.asarray(lut, np.uint8)
    idx = ((xs - off) % period).clip(0, period - 1)
    return arr[idx]


def _rainbow_img(lut, period, off, height, x_from=0, width=None):
    width = width or W
    xs = np.arange(width)
    row = _grad_row(lut, xs, period, off + x_from)
    a = np.repeat(row[None, :], height, axis=0)
    return Image.fromarray(a, "RGB")


def _ring_mask(size, box, radius, width):
    """圆角矩形描边遮罩：外框减内框。用来给胶囊上彩虹边。"""
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle(box, radius=radius, fill=255)
    inner = [box[0] + width, box[1] + width, box[2] - width, box[3] - width]
    d.rounded_rectangle(inner, radius=max(radius - width, 1), fill=0)
    return m


def build(theme_name, out_path):
    th = T.get(theme_name)
    base = _base(theme_name)
    lut = T.rainbow_lut(1024)

    fa = ImageFont.truetype(SERIF_B, FS_A)
    fb = ImageFont.truetype(SCRIPT, FS_B)
    f_chip = ImageFont.truetype(CJK_B, FS_CHIP)
    f_sub = ImageFont.truetype(SERIF_B, FS_SUB)
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))

    w_a = probe.textlength("Haoyi", font=fa)
    w_b = probe.textlength("Wang", font=fb)
    gap = 10
    x0 = int(W / 2 - (w_a + gap + w_b) / 2)
    name_period = int(w_a + gap + w_b)            # 流动周期 = 名字宽度
    y_name = 150

    cw = [int(probe.textlength(t, font=f_chip)) + 36 for t in CHIP_TEXT]
    total = sum(cw) + 9 * (len(cw) - 1)
    cx = int(W / 2 - total / 2)
    cy0, chh = 248, 34

    tag = "G E O S P A T I A L   ×   A R T I F I C I A L   I N T E L L I G E N C E"

    frames = []
    for fi in range(FRAMES):
        ph = fi / FRAMES
        off = int(name_period * ph)
        img = base.copy()

        # --- 名字：彩虹横向流动
        g = _rainbow_img(lut, name_period, off, H, x_from=x0, width=name_period)
        # 先在字底垫一层柔光。卡通背景里那道彩虹弧是浅黄的，而名字的黄色段
        # 正好会飘到它上面 —— 不垫的话有几个相位是糊的。发光比加白底框好看得多。
        glow = Image.new("L", (name_period, H), 0)
        gd = ImageDraw.Draw(glow)
        for text, font, x, y in (("Haoyi", fa, x0, y_name),
                                 ("Wang", fb, int(x0 + w_a + gap), y_name + 6)):
            gd.text((x - x0, y), text, font=font, fill=190, anchor="lm")
        glow = glow.filter(ImageFilter.GaussianBlur(11))
        img.paste(Image.new("RGB", (name_period, H), (255, 255, 255)), (x0, 0), glow)

        for text, font, x, y in (("Haoyi", fa, x0, y_name),
                                 ("Wang", fb, int(x0 + w_a + gap), y_name + 6)):
            m = Image.new("L", (name_period, H), 0)
            ImageDraw.Draw(m).text((x - x0, y), text, font=font, fill=255, anchor="lm")
            img.paste(g, (x0, 0), m)

        d = ImageDraw.Draw(img)
        # --- 名字下面一条彩虹细线
        rule_w = 620
        rule = _rainbow_img(lut, rule_w, off, 3, 0, rule_w)
        # np.array 而不是 np.asarray：asarray 对 PIL 图返回只读视图，写 alpha 会报错
        rule_a = np.array(rule.convert("RGBA"))
        # 两端对称淡出。只做单向渐入的话，有一半时间是"几乎看不见 + 右端一小截"
        # 看起来像渲染残留而不是装饰。
        t = np.linspace(-1.0, 1.0, rule_w)
        rule_a[:, :, 3] = ((1.0 - np.abs(t)) * 235).astype(np.uint8)
        img.paste(Image.fromarray(rule_a, "RGBA"),
                  (W // 2 - rule_w // 2, y_name + 52), Image.fromarray(rule_a[:, :, 3]))

        # --- 副标题
        d.text((W / 2, y_name + 74), tag, font=f_sub, fill=th["sub"], anchor="mm")

        # --- 四颗胶囊：白底 + 彩虹描边
        bar = _rainbow_img(lut, W, off, H)
        x = cx
        for t, w in zip(CHIP_TEXT, cw):
            box = [x, cy0, x + w, cy0 + chh]
            d.rounded_rectangle(box, radius=chh // 2, fill=T.hx(th["chips"][0]),
                                outline=T.hx(th["contour"]) if "contour" in th else (210, 210, 220))
            rm = _ring_mask((W, H), box, chh // 2, 2)
            img.paste(bar, (0, 0), rm)
            d.text((x + w / 2, cy0 + chh / 2 + 1), t, font=f_chip,
                   fill=th["chip_text"], anchor="mm")
            x += w + 9

        # --- 底部一条流动的彩虹条。4px 就够，再粗会变成"进度条"抢走注意力
        bottom = _rainbow_img(lut, W, off * 2, 4)
        img.paste(bottom, (0, H - 4))
        frames.append(img)

    # 全部帧共用一套调色板（逐帧 ADAPTIVE 会摧毁跨帧压缩）
    sample = Image.new("RGB", (W, H * 2))
    for i in range(2):
        sample.paste(frames[i], (0, H * i))
    pal = sample.quantize(colors=220, method=Image.MEDIANCUT)
    pf = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # disposal=1（不清屏）：背景、光晕、副标题、胶囊底每帧都一样，
    # 只有名字、细线、胶囊描边、底部彩条在变，帧间差分能吃掉大部分画面。
    # 用 disposal=2 会强制每帧整块存储，体积直接翻倍。
    pf[0].save(out_path, save_all=True, append_images=pf[1:],
               duration=MS_FRAME, loop=0, optimize=True, disposal=1)
    return out_path


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else T.ACTIVE
    out = os.path.join(ROOT, "assets", "themes", name, "banner.gif")
    build(name, out)
    print("  banner %-9s %.1f KB  (%d frames)"
          % (name, os.path.getsize(out) / 1024, FRAMES))


if __name__ == "__main__":
    main()
