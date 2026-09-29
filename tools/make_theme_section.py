# -*- coding: utf-8 -*-
"""
把「六套配色」区块渲染进 README。

为什么要脚本生成
--------------
这一块里有 6 张海报、6 个中文名、6 条配色说明，外加一个「当前」高亮。
手写的话，换主题时那个「当前」标记迟早和 ACTIVE 对不上——页面上写着"当前是樱粉"，
实际生效的却是星海，而且没有任何报错。属于最典型的静默漂移。
所以整块由 theme.py 生成，set_theme.py 每次切主题都重刷一遍，标记天然是对的。

区块用 BEGIN/END 注释夹住，重复执行只会替换中间内容，不会动 README 其他部分。
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")

BEGIN = "<!--THEMES:BEGIN-->"
END = "<!--THEMES:END-->"

# 海报是静态资产，不随主题切换变化，所以版本号固定；
# 真要重新生成海报（make_theme_posters.py）时把这里 +1，否则 camo 会一直给旧图。
POSTER_V = 1


def cell(name, th, active):
    mark = "当前 · " if active else ""
    return (
        '<td width="50%%" valign="top">'
        '<img src="./assets/themes/%s/poster.webp?v=%d" alt="%s %s" width="100%%">'
        "<br><sub><b>%s %s</b> · %s%s</sub></td>"
        % (name, POSTER_V, th["label"], name, th["label"], name, mark, th["desc"])
    )


def render(active):
    names = list(T.THEMES)
    rows = []
    for i in range(0, len(names), 2):
        pair = names[i:i + 2]
        cells = "".join(cell(n, T.THEMES[n], n == active) for n in pair)
        rows.append("<tr>%s</tr>" % cells)

    body = "\n".join(rows)
    return "\n".join([
        # 前面先垫一条分隔线，和上面每个区块的间距保持一致
        '<div align="center"><img src="./assets/divider.svg?v=3" width="520" alt=""></div>',
        "",
        "## 🎨 六套配色 · 随时切换",
        "",
        "整套主页的视觉——banner、打字机、分隔线、徽章——共用同一份配色定义，",
        "换主题是换一个值的事，banner 和徽章不会各说各话。",
        "",
        "<table>",
        body,
        "</table>",
    ])


def apply(active):
    txt = io.open(README, encoding="utf-8").read()
    block = "%s\n%s\n%s" % (BEGIN, render(active), END)

    if BEGIN in txt and END in txt:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block, txt, flags=re.S)
    else:
        new = txt.rstrip() + "\n\n" + block + "\n"

    if new == txt:
        print("    主题区块无变化")
        return False
    io.open(README, "w", encoding="utf-8").write(new)
    print("    已重写六套配色区块（当前：%s）" % T.THEMES[active]["label"])
    return True


def main():
    if len(sys.argv) > 1:
        # 手动指定主题时只重渲染，不碰徽章/资产
        apply(sys.argv[1])
    else:
        apply(T.ACTIVE)


if __name__ == "__main__":
    main()
