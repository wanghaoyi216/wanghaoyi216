# -*- coding: utf-8 -*-
"""
主题注册表 —— 整套主页视觉的"唯一配色来源"。

设计前提（2026-09-29 定稿，取代之前那版深紫红+橙金）
--------------------------------------------------
1. **白为主、粉做点缀**：整页约 75% 白，粉色集中在 banner 渐变、
   徽章、强调线这些小面积地方。深色大面积铺底会显得闷、脏、很"AI"。
2. **不要金色**：橙金 #C98A3C / #FFAF70 这一系全部去掉。
   金色和粉色同时出现会互相打架，而且金色本身偏"商务模板感"。
3. **名字用「深玫瑰 → 珊瑚粉」渐变**：在白底上既清晰又和整站粉色同源，
   不再是原来的桃红→橙金。
4. **深色只允许出现在文字上**，不作为背景。所以 banner、标题、
   徽章底色全部是浅色或白色。

改配色只改这里。banner / 打字机 / README 徽章 / streak 卡片
全部从这里取色，保证换主题时不会出现"改了 banner 忘了改徽章"。
"""

THEMES = {
    "blush": {
        "label": "胭脂",
        "desc": "白 → 淡粉",
        "bg": ("#FFFFFF", "#FDEBF2"),
        "name_grad": ["#9E2A54", "#BC3F6B", "#D25A81", "#E07197", "#EC89A9"],
        "glows": ["#FCE4EC", "#FDF0F5", "#FBE0E9"],
        "contour": "#E8A8BE",
        "star": "#F2B8C8",
        "sub": "#8E4A64",
        "chips": ["#FDF2F6", "#FDF2F6", "#FDF2F6", "#FDF2F6"],
        "chip_text": "#8C2F52",
        "accent": "#E88AA8",
        "badge": "F8D7E1",
        "badge_cta": "C9456F",
        "badge_data": "F0C3D1",
        "typing": "#8C2F52",
    },
    "peony": {
        "label": "牡丹",
        "desc": "白 → 玫粉",
        "bg": ("#FFFFFF", "#FBE4EE"),
        "name_grad": ["#861B49", "#A82A60", "#C74A78", "#DC6692", "#E77FA5"],
        "glows": ["#FCE3EE", "#FCEBF3", "#FBDDE9"],
        "contour": "#E5A0BF",
        "star": "#EEB6D0",
        "sub": "#84405F",
        "chips": ["#FCECF3", "#FCECF3", "#FCECF3", "#FCECF3"],
        "chip_text": "#7C1C43",
        "accent": "#D96A97",
        "badge": "F6D5E4",
        "badge_cta": "B32E67",
        "badge_data": "EFC4D8",
        "typing": "#7C1C43",
    },
    "sakura": {
        "label": "樱",
        "desc": "白 → 樱粉",
        "bg": ("#FFFFFF", "#FDEAF2"),
        "name_grad": ["#A32A58", "#BE4070", "#D25E8B", "#E379A2", "#ED92B4"],
        "glows": ["#FDE9F1", "#FDF0F6", "#FCE3EE"],
        "contour": "#EBAFC9",
        "star": "#F4BCD2",
        "sub": "#8C4565",
        "chips": ["#FDF0F5", "#FDF0F5", "#FDF0F5", "#FDF0F5"],
        "chip_text": "#8C2450",
        "accent": "#EA82A8",
        "badge": "F9DCE8",
        "badge_cta": "CC4A7B",
        "badge_data": "F2CBDA",
        "typing": "#8C2450",
    },
    "lilac": {
        "label": "紫藤",
        "desc": "白 → 淡紫",
        "bg": ("#FFFFFF", "#F3ECF9"),
        "name_grad": ["#5F3594", "#7C4AAF", "#9A6CC8", "#B18DD8", "#C2A5E2"],
        "glows": ["#F1E8F8", "#F5EEFB", "#EEE4F6"],
        "contour": "#CDB2E4",
        "star": "#CDB6E6",
        "sub": "#6A4E92",
        "chips": ["#F7F2FC", "#F7F2FC", "#F7F2FC", "#F7F2FC"],
        "chip_text": "#5C348C",
        "accent": "#A87BD4",
        "badge": "E6D9F5",
        "badge_cta": "8A57BE",
        "badge_data": "DCC9EE",
        "typing": "#5C348C",
    },
    "cream": {
        "label": "奶杏",
        "desc": "白 → 奶杏",
        "bg": ("#FFFFFF", "#FBF0E6"),
        "name_grad": ["#8A4E29", "#A9683C", "#C5875C", "#DCA37E", "#E9B899"],
        "glows": ["#FBF0E4", "#FDF4EC", "#F9EADC"],
        "contour": "#E0C0A2",
        "star": "#E8C9AC",
        "sub": "#8E6045",
        "chips": ["#FCF4EC", "#FCF4EC", "#FCF4EC", "#FCF4EC"],
        "chip_text": "#8A4E28",
        "accent": "#D89A6C",
        "badge": "F5E3D2",
        "badge_cta": "BC7546",
        "badge_data": "EBD6C1",
        "typing": "#8A4E28",
    },
    "mint": {
        "label": "薄荷",
        "desc": "白 → 薄荷绿",
        "bg": ("#FFFFFF", "#E8F5F0"),
        "name_grad": ["#1B5F4D", "#297D65", "#3C9B7E", "#58B39A", "#73C7B1"],
        "glows": ["#E6F4EE", "#ECF7F3", "#E2F1EB"],
        "contour": "#A5D4C4",
        "star": "#A8D8C8",
        "sub": "#3C7264",
        "chips": ["#EEF8F4", "#EEF8F4", "#EEF8F4", "#EEF8F4"],
        "chip_text": "#1F5E4D",
        "accent": "#43A88A",
        "badge": "D3EBE2",
        "badge_cta": "2E8A70",
        "badge_data": "BFE0D5",
        "typing": "#1F5E4D",
    },
}

# 当前生效主题。改这一个值 = 换掉整套配色。
ACTIVE = "blush"

# 全部徽章色（6 主题 x badge/badge_cta/badge_data = 18 个）必须两两不同。
# 为什么要较真：换色是"把别的主题色批量替换成目标色"。一旦撞车
# （比如 A 主题的 badge 色 == B 主题的 badge_cta 色），替换会连 CTA 一起改掉，
# 而页面照样正常显示 —— 只能靠这个断言兜住。
_BADGE_KEYS = ("badge", "badge_cta", "badge_data")
_seen = {}
for _t, _th in THEMES.items():
    for _k in _BADGE_KEYS:
        _c = _th[_k].lstrip("#").upper()
        if _c in _seen:
            raise ValueError(
                "徽章色撞车：%s.%s 和 %s.%s 都是 %s，换主题时会互相误伤"
                % (_seen[_c][0], _seen[_c][1], _t, _k, _c))
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
    """把 5 个色标插值成 256 级查找表（banner 的渐变文字用）。"""
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
