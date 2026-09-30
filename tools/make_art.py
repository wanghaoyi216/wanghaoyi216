# -*- coding: utf-8 -*-
"""把生成出来的卡通插画处理成 banner 用的背景素材。

为什么要单独预处理
----------------
原图 3168x1344、约 2MB，直接塞进 GIF 帧里会：
  1. 撑爆体积
  2. 抢走调色板 —— 背景细节越多，留给彩虹名字的 256 色就越少，名字会糊

所以这里一次处理到位：裁到横幅比例、提亮、降饱和、压到 1000x340 的 JPEG。
结果是"干净的浅色背景 + 醒目的彩虹字"。

关于素材来源
------------
这张图是用本机 mcode-tools 的图像生成能力现生成的，自带版权，不含
任何机构标识、校徽或商标（提示词里明确排除了 text / logo / emblem）。
不要去网上扒现成的卡通图打包进来。

重跑方式：把新的原图放到 preview/cartoon-src.jpg，然后
    python tools/make_art.py
"""
import os
import sys

from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "preview", "cartoon-src.jpg")
OUT = os.path.join(ROOT, "assets", "art", "cartoon.jpg")
W, H = 1000, 340
TOP = 120          # 裁剪窗口上沿；取 120 能让彩虹弧和云朵都完整
BRIGHT = 1.05      # 提亮
WHITE_MIX = 0.13   # 往白里混的比例


def prepare():
    if not os.path.exists(SRC):
        raise SystemExit("找不到原图 %s\n"
                         "把生成好的 21:9 卡通插画存成这个文件名再重跑。" % SRC)
    art = Image.open(SRC).convert("RGB")

    nh = int(art.width / (W / H))
    top = max(0, min(art.height - nh, TOP))
    art = art.crop((0, top, art.width, top + nh)).resize((W, H), Image.LANCZOS)

    art = ImageEnhance.Brightness(art).enhance(BRIGHT)
    art = Image.blend(art, Image.new("RGB", (W, H), (255, 255, 255)), WHITE_MIX)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    art.save(OUT, "JPEG", quality=86, optimize=True, progressive=True)
    return OUT


if __name__ == "__main__":
    p = prepare()
    im = Image.open(p)
    print("  art %s  %dx%d  %.1f KB" % (p, im.width, im.height, os.path.getsize(p) / 1024))
