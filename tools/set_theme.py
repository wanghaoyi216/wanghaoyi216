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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")

# 主题目录里的文件名 -> README 实际引用的文件名
# （主题目录不带 -dark 后缀，根目录带；这个映射错了会导致"版本号 bump 了但图没换"的静默失败）
LOCAL_ASSETS = {
    "banner.gif": "banner-dark.gif",
    "typing.gif": "typing-dark.gif",
    "divider.svg": "divider.svg",
}
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
    for key in ("badge", "badge_cta", "badge_data"):
        tgt = th[key].lstrip("#").upper()
        for other in T.THEMES.values():
            src_c = other[key].lstrip("#").upper()
            if src_c == tgt:
                continue
            txt = txt.replace("-" + src_c + "&style=for-the-badge", "-" + tgt + "&style=for-the-badge")
            txt = txt.replace("color=" + src_c + "&style=for-the-badge", "color=" + tgt + "&style=for-the-badge")
            txt = txt.replace("color=" + src_c + "&label=", "color=" + tgt + "&label=")
            txt = re.sub(r"(-)" + src_c + r"(&logo=)", r"\g<1>" + tgt + r"\g<2>", txt)

    # bump 本地图的缓存版本
    for a in BUMP_TARGETS:
        v = next_version(txt, a)
        if v:
            txt = re.sub(re.escape(a) + r"\?v=\d+", "%s?v=%d" % (a, v), txt)

    open(README, "w", encoding="utf-8").write(txt)
    set_active(name)
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
            import make_banner_gif, make_typing_gif, make_divider
            base = os.path.join(ROOT, "assets", "themes", k)
            make_banner_gif.build(k, os.path.join(base, "banner.gif"))
            make_typing_gif.build(k, os.path.join(base, "typing.gif"))
            make_divider.build(k, os.path.join(base, "divider.svg"))
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
