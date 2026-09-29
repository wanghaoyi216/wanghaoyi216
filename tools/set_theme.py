# -*- coding: utf-8 -*-
"""
主题切换器。

用法：
    D:\\Anaconda3\\python.exe tools\\set_theme.py            # 列出所有主题
    D:\\Anaconda3\\python.exe tools\\set_theme.py warm       # 切到 warm 并生成
    D:\\Anaconda3\\python.exe tools\\set_theme.py all        # 一次性生成全部主题

切主题会做四件事：
    1. 改 tools/theme.py 里的 ACTIVE
    2. 把该主题的 banner/typing/divider 复制到 assets/ 根目录（README 引用的是这里）
    3. 按主题重写 README 里所有 shields.io / komarev 的徽章颜色
    4. bump README 里三张本地图的 ?v=N（camo 按 URL 缓存，不 bump 访客看不到新图）
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T
import make_headers as _headers
import make_theme_section as _section

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")

# 主题目录里的文件名 -> README 实际引用的文件名
# （主题目录不带 -dark 后缀，根目录带；这个映射错了会导致"版本号 bump 了但图没换"的静默失败）
LOCAL_ASSETS = {
    "banner.gif": "banner-dark.gif",
    "typing.gif": "typing-dark.gif",
    "divider.svg": "divider.svg",
}
# 区块标题图：命名规则固定，单独枚举而不是并进上面的字典，
# 这样 bump 缓存版本号时不用把 7 个文件名一个个写死。
HEADERS = [s for s, _, _ in _headers.SECTIONS]
LOCAL_ASSETS.update({"h-%s.webp" % s: "header-%s.webp" % s for s in HEADERS})
BUMP_TARGETS = list(LOCAL_ASSETS.values())


def usage():
    print("可用主题：")
    for k, v in T.THEMES.items():
        mark = " ← 当前" if k == T.ACTIVE else ""
        print("  %-8s %s%s" % (k, v["label"], mark))
    print("\n用法：python tools/set_theme.py <主题名> | all")


def set_active(name):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "theme.py")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r'^ACTIVE\s*=\s*".*?"', 'ACTIVE = "%s"' % name, s, flags=re.M)
    open(p, "w", encoding="utf-8").write(s)


def next_version(txt, asset):
    m = re.search(re.escape(asset) + r"\?v=(\d+)", txt)
    if not m:
        return None
    return int(m.group(1)) + 1


# streak-stats 卡片：全站唯一不受主题控制的第三方图。
# 它支持 background/border/stroke/ring/fire/sideNums/sideLabels/title 八个自定义色，
# 所以不必换掉它（那会丢掉实时数据），直接把它染成当前主题即可——
# 默认 theme=github-dark 的亮绿色是整页唯一的冷色，也是"撞色"的来源。
STREAK_RE = re.compile(r"https://streak-stats\.demolab\.com\?[^\s\")']+")


def streak_url(th, user="wanghaoyi216"):
    c = lambda v: v.lstrip("#").upper()
    return ("https://streak-stats.demolab.com?user=%s&hide_border=true"
            "&background=%s&border=%s&stroke=%s&ring=%s&fire=%s"
            "&sideNums=%s&sideLabels=%s&title=%s"
            % (user, c(th["bg"][0]), c(th["bg"][0]), c(th["chips"][0]), c(th["contour"]),
               c(th["accent"]), c(th["sub"]), c(th["badge_cta"]), c(th["sub"])))


def leftover_colors(txt, name):
    """换完色之后扫一遍 README，看还有没有别的主题色残留。

    这是给"静默失败"兜底的：替换逻辑只要有一个分隔符没覆盖对，
    页面不会报错、图也照常显示，只有颜色悄悄没换。这里把它变成硬失败。
    """
    th = T.get(name)
    mine = {th[k].lstrip("#").upper() for k in ("badge", "badge_cta", "badge_data")}
    bad = []
    for key in ("badge", "badge_cta", "badge_data"):
        for other_name, other in T.THEMES.items():
            c = other[key].lstrip("#").upper()
            if c in mine or c not in txt:
                continue
            n = len(re.findall(r"(-|color=)" + c + r"(?=[?&])", txt))
            if n:
                bad.append("  %s 的 %s 色 %s 仍残留 %d 处" % (other_name, key, c, n))
    return bad


def apply_theme(name):
    th = T.get(name)
    src = os.path.join(ROOT, "assets", "themes", name)
    dst = os.path.join(ROOT, "assets")

    for src_name, dst_name in LOCAL_ASSETS.items():
        s = os.path.join(src, src_name)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(dst, dst_name))
        else:
            raise FileNotFoundError("主题 %s 缺少 %s，请先跑 set_theme.py all" % (name, s))

    txt = open(README, encoding="utf-8").read()

    # 徽章配色：把已知所有主题的徽章色统一映射到目标主题
    #
    # shields.io 的颜色参数有三种落点，全都要覆盖，漏一个就是"图换了徽章没换"：
    #   路径段式   /badge/Python-A8485C?style=for-the-badge   颜色后面跟的是 ?
    #   查询参数式 ?label=Stars&color=6B3A3F&style=...        颜色前面有 color=，后面跟 &
    #   旧写法     ...&color=6B3A3F&label=...                颜色后面跟 &
    #
    # 坑：路径段式里颜色后面那个分隔符是 ?(0x3F) 不是 &(0x26)。
    # shields.io 两者都认（都是查询串分隔符），所以线上徽章显示正常，
    # 肉眼完全看不出问题，只有按 & 匹配替换的脚本会静默失效。
    # 判据：改完必须能打印出替换处数，全 0 就是没换成功，别看"没报错"就当成功。
    for key in ("badge", "badge_cta", "badge_data"):
        tgt = th[key].lstrip("#").upper()
        for other in T.THEMES.values():
            src_c = other[key].lstrip("#").upper()
            if src_c == tgt:
                continue
            # 要求颜色前面是 - 或 color=，后面紧跟 ? 或 &，避免误伤无关文本
            txt, n = re.subn(r"(-|color=)" + src_c + r"(?=[?&])", r"\g<1>" + tgt, txt)
            if n:
                print("    %-7s -> %-7s  %d 处" % (src_c, tgt, n))

    # bump 本地图的缓存版本
    for a in BUMP_TARGETS:
        v = next_version(txt, a)
        if v:
            txt = re.sub(re.escape(a) + r"\?v=\d+", "%s?v=%d" % (a, v), txt)

    # streak 卡片换色（全站最后一个不受主题控制的元素）
    txt, n = STREAK_RE.subn(streak_url(th), txt)
    if n != 1:
        raise RuntimeError("README 里应该正好有 1 个 streak 卡片，实际 %d 个" % n)

    bad = leftover_colors(txt, name)
    if bad:
        raise RuntimeError("换色不完整，README 未写入：\n" + "\n".join(bad))

    open(README, "w", encoding="utf-8").write(txt)
    set_active(name)

    # 「六套配色」区块由脚本重渲，保证页面上的"当前"标记和 ACTIVE 永远一致。
    # 手写这个标记迟早会和实际主题对不上，而且不会报任何错。
    _section.apply(name)

    return th


def main():
    if len(sys.argv) < 2:
        usage()
        return
    arg = sys.argv[1]
    if arg in ("-h", "--help", "list"):
        usage()
        return
    if arg == "all":
        for k in T.THEMES:
            if k != T.ACTIVE:
                print("  已生成主题：%s (%s)" % (k, T.THEMES[k]["label"]))
            import make_banner_gif, make_typing_gif, make_divider, make_theme_posters
            base = os.path.join(ROOT, "assets", "themes", k)
            make_banner_gif.build(k, os.path.join(base, "banner.gif"))
            make_typing_gif.build(k, os.path.join(base, "typing.gif"))
            make_divider.build(k, os.path.join(base, "divider.svg"))
            make_theme_posters.build(k)
            _headers.build(k)
        _section.apply(T.ACTIVE)
        print("\n全部主题已生成到 assets/themes/<主题名>/")
        usage()
        return

    th = apply_theme(arg)
    print("  已切换到主题：%s（%s）" % (arg, th["label"]))
    print("  徽章配色：%s / CTA %s / 数据 %s" % (th["badge"], th["badge_cta"], th["badge_data"]))
    print("  已更新 assets/ 下的成品与 README 徽章色、缓存版本号")
    print("\n  下一步：git add -A; git commit -m \"theme: %s\"; git push" % arg)


if __name__ == "__main__":
    main()
