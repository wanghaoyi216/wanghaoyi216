# -*- coding: utf-8 -*-
"""
区块标题图（WebP，静态）—— 把纯 markdown 的 `## 关于我` 换成带设计感的标题条。
配色来自 tools/theme.py，跟着主题一起切。

为什么是光栅而不是 SVG
--------------------
SVG 里放中文要转矢量路径（fontTools），但 emoji 转不了路径：
Segoe UI Emoji 是 COLR/CPAL 彩色字体，glyf 表基本是空的，转出来是空白方块。
PIL 12 带 embedded_color=True 可以直接画彩色 emoji（实测 538 色 vs 单色 254 色），
所以标题图走光栅。为了控制体积，2 倍渲染后存 WebP（5~9KB/张）而不是 PNG。

为什么标题条自带深色底
--------------------
GitHub README 可以切浅色模式。深色 hero 是图片所以无所谓，但标题如果做成
"亮色渐变字 + 透明底"，访客切到浅色主题就全是白字白底、完全看不见。
所以每个标题做成一枚深色胶囊，浅色深色模式下都读得出来。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = r"C:\Windows\Fonts"
CJK_B = os.path.join(FDIR, "msyhbd.ttc")
EMOJI = os.path.join(FDIR, "seguiemj.ttf")

W, H = 780, 56          # 逻辑尺寸
SS = 2                  # 2 倍渲染，GitHub 上按 50% 显示 = 视网膜屏清晰
PAD_X, EMOJI_GAP, TEXT_GAP = 20, 9, 11
FS_TITLE, FS_EMOJI = 25, 24

# (slug, emoji, 标题)
SECTIONS = [
    ("status", "\U0001F52D", "现在"),
    ("about", "\U0001F9ED", "关于我"),
    ("projects", "\U0001F680", "精选项目"),
    ("stack", "\U0001F6E0\uFE0F", "技术栈"),
    ("streak", "\U0001F4CA", "贡献轨迹"),
    ("contact", "\U0001F4EB", "找到我"),
    ("themes", "\U0001F3A8", "六套配色"),
]


def _grad_lut(th, x0, x1, w, h):
    """在全局横向区间 [x0, x1] 内取色，输出 w x h。

    刻意按"全局 x"而不是"图内 x"取色：标题的渐变要横跨整段文字，
    而贴图时用的是文字墨迹的裁剪区（比整段 advance 略窄），
    两者对不上就会报 images do not match。传区间就自然对齐了。
    """
    stops = [T.hx(c) for c in th["name_grad"]]
    img = Image.new("RGB", (max(w, 1), max(h, 1)))
    px = img.load()
    span = max(x1 - x0, 1)
    for x in range(img.width):
        p = min(max((x0 + x) / span, 0.0), 1.0) * (len(stops) - 1)
        i = min(int(p), len(stops) - 2)
        k = p - i
        k = k * k * (3 - 2 * k)                 # smoothstep，避免色标处出现折角
        a, b = stops[i], stops[i + 1]
        c = tuple(int(a[m] + (b[m] - a[m]) * k) for m in range(3))
        for y in range(img.height):
            px[x, y] = c
    return img


def _sparkle(d, cx, cy, r, color, alpha=255):
    d.line([(cx - r, cy), (cx + r, cy)], fill=color, width=1)
    d.line([(cx, cy - r), (cx, cy + r)], fill=color, width=1)
    d.ellipse([cx - .6, cy - .6, cx + .6, cy + .6], fill=color)


def build(theme_name, slug=None, out_dir=None):
    th = T.get(theme_name)
    targets = [(s, e, t) for (s, e, t) in SECTIONS] if slug is None else \
              [(x[0], x[1], x[2]) for x in SECTIONS if x[0] == slug]
    if not targets:
        raise KeyError("未知区块 %r，可选：%s" % (slug, [s for s, _, _ in SECTIONS]))

    f_title = ImageFont.truetype(CJK_B, FS_TITLE * SS)
    f_emoji = ImageFont.truetype(EMOJI, FS_EMOJI * SS)
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))

    made = []
    for s, emo, title in targets:
        tw = int(probe.textlength(title, font=f_title))
        ew = int(probe.textlength(emo, font=f_emoji))
        pill_w = PAD_X * 2 + ew + EMOJI_GAP + tw + 0
        pill_h = FS_TITLE + 20
        px0, py0 = 0, (H - pill_h) // 2

        img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))

        # --- 胶囊底：主题底色 + 轮廓描边 + 外发光
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.rounded_rectangle(
            [px0 * SS - 10, py0 * SS - 10, (px0 + pill_w) * SS + 10, (py0 + pill_h) * SS + 10],
            radius=(pill_h // 2) * SS, fill=T.hx(th["glows"][0]) + (70,))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9 * SS)))

        d = ImageDraw.Draw(img)
        d.rounded_rectangle(
            [px0 * SS, py0 * SS, (px0 + pill_w) * SS, (py0 + pill_h) * SS],
            radius=(pill_h // 2) * SS,
            fill=T.hx(th["bg"][0]) + (246,),
            outline=T.hx(th["contour"]) + (150,), width=SS)

        # --- emoji + 渐变标题
        tx = (px0 + PAD_X + ew + EMOJI_GAP) * SS
        ty = (H / 2) * SS
        d.text((tx - ew * SS, ty), emo, font=f_emoji, embedded_color=True, anchor="lm")

        mask = Image.new("L", img.size, 0)
        md = ImageDraw.Draw(mask)
        md.text((tx, ty), title, font=f_title, fill=255, anchor="lm")
        bb = tuple(int(round(v)) for v in md.textbbox((tx, ty), title, font=f_title, anchor="lm"))
        g = _grad_lut(th, bb[0], bb[0] + tw * SS, bb[2] - bb[0], bb[3] - bb[1])
        img.paste(g, (bb[0], bb[1]), mask.crop(bb))

        # --- 右侧延伸的渐变细线 + 星光
        lx0 = (px0 + pill_w + 12) * SS
        # 只画剩余空间的一半：通栏画出来像一条进度条，视线会被从标题上拽走
        lw = max(int((W * SS - lx0) * 0.5), 1)
        lh = 3 * SS
        grad = _grad_lut(th, lx0, lx0 + lw, lw, 1)
        line = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
        lp = line.load()
        for x in range(lw):
            a = int(210 * (1 - x / max(lw, 1)) ** 2.0)
            r, g_, b = grad.load()[x, 0]
            for y in range(lh):
                lp[x, y] = (r, g_, b, a)
        img.alpha_composite(line, (lx0, int((H / 2 - 1.5) * SS)))

        for (fx, fy, fr) in ((0.30, 0.26, 1.7), (0.44, 0.78, 1.4), (0.61, 0.22, 1.9), (0.78, 0.74, 1.5)):
            _sparkle(d, fx * W * SS, fy * H * SS, fr * SS, T.hx(th["star"]) + (190,))

        out = os.path.join(out_dir or os.path.join(ROOT, "assets", "themes", theme_name),
                           "h-%s.webp" % s)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        # 必须保留 RGBA 直接存：一旦 convert("RGB")，alpha 会被丢掉，
        # 原本透明的画布变成纯黑，GitHub 浅色模式下一排黑条。
        img.save(out, "WEBP", quality=92, method=6)
        made.append(out)
    return made


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else T.ACTIVE
    for p in build(name):
        print("  header %-34s %5.1f KB" % (os.path.basename(p), os.path.getsize(p) / 1024))


if __name__ == "__main__":
    main()
