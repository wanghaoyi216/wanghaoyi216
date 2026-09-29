# -*- coding: utf-8 -*-
"""
主题注册表 —— 整套主页视觉的"唯一配色来源"。

改配色只改这里。banner / 打字机 / 分隔线 / README 徽章
全部从这里取色，保证任何时候换主题都不会出现"改了 banner 忘了改徽章"的割裂。

每个主题需要定义：
  label      中文名（展示用）
  bg         (顶, 底) 页面底色，竖直渐变
  name_grad  名字色带，5 个色标，桃红->橙金这种
  glows      三层光晕颜色
  contour    等高线颜色
  star       星光颜色
  sub        副标题文字色
  chips      四个胶囊的底色
  chip_text  胶囊文字色
  accent     底部强调线
  badge      徽章主色
  badge_cta  CTA 按钮色（金色系做视觉焦点）
  badge_data 数据徽章色（要比 badge 更暗，退到次要层）
  typing     打字机文字色
"""

THEMES = {
    "warm": {
        "label": "暖阳",
        "desc": "桃红 → 橙金",
        "bg": ("#1A0F21", "#4E2830"),
        "name_grad": ["#FF8A8F", "#FFB07A", "#FFE9C0", "#FFC56C", "#F28A3A"],
        "glows": ["#FF8A76", "#FFC678", "#FFA8C8"],
        "contour": "#FFCBA4",
        "star": "#FFECC8",
        "sub": "#FFE0C8",
        "chips": ["#602C2E", "#763828", "#303E60", "#2E4E3E"],
        "chip_text": "#FFE4D0",
        "accent": "#FFAF70",
        "badge": "A8485C",
        "badge_cta": "C98A3C",
        "badge_data": "6B3A3F",
        "typing": "#FFD9A8",
    },
    "aurora": {
        "label": "极光",
        "desc": "薄荷 → 冰蓝",
        "bg": ("#04141F", "#0B3A44"),
        "name_grad": ["#3FE0B0", "#7FF0D8", "#E8FFFB", "#5AC8E8", "#2E7FD4"],
        "glows": ["#2FD4A8", "#48B8E8", "#8C7BE8"],
        "contour": "#8FE8DC",
        "star": "#DCFFF6",
        "sub": "#BDF0E4",
        "chips": ["#12484C", "#14526A", "#1B3F6E", "#1F5240"],
        "chip_text": "#D8FFF4",
        "accent": "#3FE0B0",
        "badge": "17786A",
        "badge_cta": "2A9D8F",
        "badge_data": "14484C",
        "typing": "#A8F0DC",
    },
    "sakura": {
        "label": "樱粉",
        "desc": "樱粉 → 淡紫",
        "bg": ("#1C0E1C", "#4A1F3A"),
        "name_grad": ["#FF9EC4", "#FFC2DA", "#FFF0F6", "#E0A8F0", "#A87CD4"],
        "glows": ["#FF8FB8", "#E0A0E8", "#FFC0D8"],
        "contour": "#F5B8D4",
        "star": "#FFE4F0",
        "sub": "#F8D0E4",
        "chips": ["#5E2440", "#6A2C52", "#402A66", "#5A2A46"],
        "chip_text": "#FFE2F0",
        "accent": "#FF9EC4",
        "badge": "A8447C",
        "badge_cta": "C96BA8",
        "badge_data": "6B2C4C",
        "typing": "#FFC8E0",
    },
    "nebula": {
        "label": "星海",
        "desc": "靛蓝 → 洋红",
        "bg": ("#0A0A24", "#241548"),
        "name_grad": ["#5A8CFF", "#8C6CFF", "#F0EEFF", "#C86CFF", "#FF5A9C"],
        "glows": ["#5A6CFF", "#A84CFF", "#FF5A9C"],
        "contour": "#B0A8F0",
        "star": "#E8E4FF",
        "sub": "#C4C0F0",
        "chips": ["#20205A", "#2C2470", "#4A2470", "#242E6A"],
        "chip_text": "#E4E0FF",
        "accent": "#7A7CFF",
        "badge": "4A48A8",
        "badge_cta": "8C5CD4",
        "badge_data": "2C2A62",
        "typing": "#C8C0FF",
    },
    "mint": {
        "label": "薄荷",
        "desc": "薄荷绿 → 青柠",
        "bg": ("#041A18", "#0E4038"),
        "name_grad": ["#7FF0C0", "#A8F5D8", "#F0FFF8", "#5CD8C0", "#2E9C8A"],
        "glows": ["#4CD8B0", "#68E0C8", "#9CE8D0"],
        "contour": "#A8E8D8",
        "star": "#E8FFF8",
        "sub": "#C8F0E4",
        "chips": ["#124A42", "#16544E", "#1E5A4A", "#2A5A3E"],
        "chip_text": "#DFFFF2",
        "accent": "#5CE0B8",
        "badge": "1E7A66",
        "badge_cta": "2EA88A",
        "badge_data": "#154A44".lstrip("#"),
        "typing": "#B4F0DC",
    },
    "noir": {
        "label": "墨金",
        "desc": "哑光金 · 黑底",
        "bg": ("#0A0A0A", "#1E1A14"),
        "name_grad": ["#B08A3C", "#D4B05C", "#FFF6DC", "#E0C070", "#8A6A2A"],
        "glows": ["#B08A3C", "#8A6A2A", "#D4B05C"],
        "contour": "#C4A468",
        "star": "#FFF0C4",
        "sub": "#E0CFA8",
        "chips": ["#26221A", "#2E2820", "#1E2228", "#22261E"],
        "chip_text": "#F0E4C4",
        "accent": "#D4B05C",
        "badge": "6E5A2A",
        "badge_cta": "A88A3C",
        "badge_data": "#3A342A".lstrip("#"),
        "typing": "#E8D8A8",
    },
}

# 当前生效主题。改这一个值 = 换掉整套配色。
ACTIVE = "warm"

# 全部徽章色（18 个 = 6 主题 × badge/badge_cta/badge_data）必须两两不同。
# 为什么要较真：set_theme.py 换色是"把别的主题色批量替换成目标色"。
# 一旦有颜色撞车（比如 A 主题的 badge 色 == B 主题的 badge_cta 色），
# 替换就会把 CTA 按钮一起改掉，而页面照样正常显示——只能靠这个断言兜住。
_BADGE_KEYS = ("badge", "badge_cta", "badge_data")
_seen = {}
for _t, _th in THEMES.items():
    for _k in _BADGE_KEYS:
        _c = _th[_k].lstrip("#").upper()
        if _c in _seen:
            raise ValueError(
                "徽章色撞车：%s.%s 和 %s.%s 都是 %s，换主题时会互相误伤"
                % (_seen[_c][0], _seen[_c][1], _t, _k, _c)
            )
        _seen[_c] = (_t, _k)
del _BADGE_KEYS, _seen, _t, _th, _k, _c


def get(name=None):
    name = name or ACTIVE
    if name not in THEMES:
        raise KeyError("未知主题 %r，可选：%s" % (name, ", ".join(THEMES)))
    return THEMES[name]


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def name_lut(theme, n=256):
    """把 5 个色标插值成 256 级查找表，供波浪渐变场用。"""
    import numpy as np
    stops = [(i / (len(theme["name_grad"]) - 1), hx(c)) for i, c in enumerate(theme["name_grad"])]
    lut = np.zeros((n, 3))
    for i in range(n):
        t = i / (n - 1)
        for j in range(len(stops) - 1):
            p0, c0 = stops[j]
            p1, c1 = stops[j + 1]
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0)
                k = k * k * (3 - 2 * k)
                lut[i] = [c0[m] + (c1[m] - c0[m]) * k for m in range(3)]
                break
        else:
            lut[i] = stops[-1][1]
    return lut
