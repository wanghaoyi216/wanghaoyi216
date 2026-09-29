# -*- coding: utf-8 -*-
"""
主题切换器。

用法：
    D:\\Anaconda3\\python.exe tools\\set_theme.py            # 列出所有主题
    D:\\Anaconda3\\python.exe tools\\set_theme.py blush      # 切到某个主题
    D:\\Anaconda3\\python.exe tools\\set_theme.py all        # 一次性生成全部主题

切主题会做四件事：
    1. 改 tools/theme.py 里的 ACTIVE
    2. 把该主题的 banner.svg / typing.gif 复制到 assets/ 根目录（README 引用的是这里）
    3. 按主题重写 README 里所有 shields.io / komarev 的徽章颜色，以及 streak 卡片 URL
    4. bump README 里两张本地图的 ?v=N（camo 按 URL 缓存，不 bump 访客看不到新图）
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")

# 主题目录里的文件名 -> README 实际引用的文件名（现在同名，映射是恒等的）
LOCAL_ASSETS = {
    "banner.svg": "banner.svg",
    "typing.gif": "typing.gif",
}
BUMP_TARGETS = list(LOCAL_ASSETS.values())

# streak 卡片是全站唯一的第三方图，它支持八个自定义色参数，
# 所以不用换掉它（那会丢掉实时贡献数据），直接染成主题色。
# 不染色的话它默认是亮绿色，在浅粉页面里格外扎眼。
STREAK_RE = re.compile(r"https://streak-stats\.demolab\.com\?[^\s\")']+")

# shields.io 里颜色可能出现在两处：路径段的 -颜色，和查询串的 color= / labelColor=。
# 注意 labelColor 的 C 是大写，写成 r"color=" 会漏掉它 —— 换主题时 value 变了、
# label 侧还留着上一套的颜色，深色模式下那块就糊进背景里。
# 所以这里显式列出两个参数名，不要用 re.I 整体忽略大小写（那会连十六进制值一起放宽）。
_COLOR_KEY = r"(-|(?:labelColor|color)=)"


def _color_re(c):
    return _COLOR_KEY + c + r"(?=[?&])"


def usage():
    print("可用主题：")
    for k, v in T.THEMES.items():
        mark = " ← 当前" if k == T.ACTIVE else ""
        print("  %-8s %-6s %-14s%s" % (k, v["label"], v["desc"], mark))
    print("\n用法：python tools/set_theme.py <主题名> | all")


def set_active(name):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "theme.py")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r'^ACTIVE\s*=\s*".*?"', 'ACTIVE = "%s"' % name, s, flags=re.M)
    open(p, "w", encoding="utf-8").write(s)


def next_version(txt, asset):
    m = re.search(re.escape(asset) + r"\?v=(\d+)", txt)
    return int(m.group(1)) + 1 if m else None


def streak_url(th, user="wanghaoyi216"):
    c = lambda v: v.lstrip("#").upper()
    # 背景取 bg[1]（浅粉）而不是 bg[0]（纯白）��纯白卡片放在 GitHub 白色页面上等于隐形。
    # 浅色主题下这张卡要能看出是一张"卡"，所以底比页面略深一点。
    # currStreakLabel 不能少：中间那列的 "Current Streak" 文字是对方
    # 硬编码的 #FB8C00（橙金），不传这个参数就改不掉 —— 而橙色正是要避开的色系。
    return ("https://streak-stats.demolab.com?user=%s&hide_border=false"
            "&background=%s&border=%s&stroke=%s&ring=%s&fire=%s"
            "&sideNums=%s&sideLabels=%s&title=%s&currStreakLabel=%s"
            % (user, c(th["bg"][1]), c(th["contour"]), c(th["contour"]), c(th["accent"]),
               c(th["chip_text"]), c(th["typing"]), c(th["badge_cta"]), c(th["typing"]),
               c(th["chip_text"])))


def leftover_colors(txt, name):
    """换完色之后扫一遍 README，看还有没有别的主题色残留。

    给"静默失败"兜底：替换逻辑只要有一个分隔符没覆盖对，页面不会报错、
    图也照常显示，只有颜色悄悄没换。这里把它变成硬失败。
    """
    th = T.get(name)
    mine = {th[k].lstrip("#").upper() for k in ("badge", "badge_cta", "badge_data")}
    bad = []
    for key in ("badge", "badge_cta", "badge_data"):
        for other_name, other in T.THEMES.items():
            c = other[key].lstrip("#").upper()
            if c in mine or c not in txt:
                continue
            n = len(re.findall(_color_re(c), txt))
            if n:
                bad.append("  %s 的 %s 色 %s 仍残留 %d 处" % (other_name, key, c, n))
    return bad


def apply_theme(name):
    th = T.get(name)
    src = os.path.join(ROOT, "assets", "themes", name)
    dst = os.path.join(ROOT, "assets")

    for src_name, dst_name in LOCAL_ASSETS.items():
        s = os.path.join(src, src_name)
        if not os.path.exists(s):
            raise FileNotFoundError("主题 %s 缺少 %s，请先跑 set_theme.py all" % (name, s))
        shutil.copy2(s, os.path.join(dst, dst_name))

    txt = open(README, encoding="utf-8").read()

    # 徽章配色。shields.io 的颜色有三种落点，必须都覆盖：
    #   路径段式   /badge/Python-A8485C?style=for-the-badge   颜色后面跟的是 ?
    #   查询参数式 ?label=Stars&color=6B3A3F&style=...        颜色前面有 color=，后面跟 &
    # 路径段式里颜色后面那个分隔符是 ?(0x3F) 不是 &(0x26)，两者 shields.io 都认，
    # 所以线上显示完全正常、肉眼看不出问题，只有按 & 匹配的脚本会静默失效。
    for key in ("badge", "badge_cta", "badge_data"):
        tgt = th[key].lstrip("#").upper()
        for other in T.THEMES.values():
            src_c = other[key].lstrip("#").upper()
            if src_c == tgt:
                continue
            txt, n = re.subn(_color_re(src_c), r"\g<1>" + tgt, txt)
            if n:
                print("    %-7s -> %-7s  %d 处" % (src_c, tgt, n))

    txt, n = STREAK_RE.subn(streak_url(th), txt)
    if n != 1:
        raise RuntimeError("README 里应该正好有 1 个 streak 卡片，实际 %d 个" % n)

    for a in BUMP_TARGETS:
        v = next_version(txt, a)
        if v:
            txt = re.sub(re.escape(a) + r"\?v=\d+", "%s?v=%d" % (a, v), txt)

    bad = leftover_colors(txt, name)
    if bad:
        raise RuntimeError("换色不完整，README 未写入：\n" + "\n".join(bad))

    open(README, "w", encoding="utf-8").write(txt)
    set_active(name)
    return th


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "list"):
        usage()
        return
    arg = sys.argv[1]

    if arg == "all":
        import make_banner, make_typing_gif
        for k in T.THEMES:
            base = os.path.join(ROOT, "assets", "themes", k)
            make_banner.build(k, os.path.join(base, "banner.svg"))
            make_typing_gif.build(k, os.path.join(base, "typing.gif"))
            print("  已生成主题：%s (%s)" % (k, T.THEMES[k]["label"]))
        print("\n全部主题已生成到 assets/themes/<主题名>/")
        usage()
        return

    th = apply_theme(arg)
    print("\n  已切换到主题：%s（%s · %s）" % (arg, th["label"], th["desc"]))
    print("  徽章配色：%s / CTA %s / 数据 %s" % (th["badge"], th["badge_cta"], th["badge_data"]))
    print("  已更新 assets/ 下的成品、README 徽章色与缓存版本号")
    print("\n  下一步：git add -A; git commit -m \"theme: %s\"; git push" % arg)


if __name__ == "__main__":
    main()
