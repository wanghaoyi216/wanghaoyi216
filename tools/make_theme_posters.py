# -*- coding: utf-8 -*-
"""
六套主题的静态海报（WebP）—— 用来在 README 的 <details> 里一次性展示全部主题。

为什么不用 GIF
--------------
六张 banner GIF 一共约 2.5MB。放进 README 即使包在折叠的 <details> 里，
浏览器多半照样会把 src 里的图全拉下来，首屏白白多几 MB。
海报取的是同一套绘制逻辑的第 0 帧，等比缩到 640 宽再存 WebP，单张 20KB 上下。

为什么海报和 banner 必须同源
--------------------------
如果海报另写一套绘制代码，过两个月配色一改就会变成"海报和 banner 长得不一样"。
所以这里直接 import make_banner_gif.render_frames()，永远跟着主题走。
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T
import make_banner_gif as BG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTER_W = 640


def build(theme_name, out_path=None):
    if out_path is None:
        out_path = os.path.join(ROOT, "assets", "themes", theme_name, "poster.webp")
    frame = BG.render_frames(theme_name)[0]          # 第 0 帧：星光最亮的一批
    h = round(frame.height * POSTER_W / frame.width)
    poster = frame.resize((POSTER_W, h), Image.LANCZOS)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    poster.save(out_path, "WEBP", quality=82, method=6)
    return out_path


def main():
    total = 0
    for name in T.THEMES:
        p = build(name)
        # 显式报错而不是 os.path.exists 静默跳过：文件没生成却当成功，
        # 线上就是一堆裂图，而本地一切正常。
        if not os.path.exists(p) or os.path.getsize(p) < 2000:
            raise RuntimeError("海报生成失败或过小：%s" % p)
        kb = os.path.getsize(p) / 1024
        total += kb
        print("  poster  %-8s %6.1f KB" % (name, kb))
    print("  ---- 合计 %.1f KB" % total)


if __name__ == "__main__":
    main()
