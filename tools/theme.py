# -*- coding: utf-8 -*-
"""
主题注册表 —— 整套主页视觉的"唯一配色来源"。

设计前提（2026-09-30 定稿）
---------------------------
1. **彩虹流动**。名字的填充是一条完整光谱，横向缓慢流动；
   底部再有一条同样在流动的彩虹细线。这是全站唯一会动的地方之一。
2. **白底 + 淡彩晕**。大面积保持白，只在背景铺三团很淡的粉彩光晕。
   整页做成彩虹背景会俗气；只让名字和细线带彩虹，冲击力够但不吵。
3. **不用粉色主导**。上一版白→淡粉被反馈"太娘炮"，
   所以每套主题的底色晕和强调色都必须**跨色相**（至少含暖 + 冷两个方向）。
4. **深色只出现在文字上**，不作为背景。

六套主题共用 `RAINBOW` 这条色带 —— 它是这个主页的签名，不随主题变化。
各主题的差异是背景光晕 `wash` 和强调色，适合"换个心情"而不是"换个风格"。
"""

# 全站共用的彩虹色带。首尾同色 —— 横向平移一整圈后能无缝接上。
RAINBOW = ["#FF5C7A", "#FF9A3C", "#F7C948", "#5FD97E",
           "#35C4E4", "#5B7BF5", "#A96BEE"]

THEMES = {
    "spectrum": {
        "label": "全彩",
        "desc": "全光谱 · 多色光晕",
        "bg": ("#FFFFFF", "#F7F4FB"),
        "wash": ["#FFE3EC", "#E2ECFF", "#E6FBF1"],
        "sub": "#4A4A57",
        "chips": ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
        "chip_text": "#3D3D48",
        "accent": "#5B7BF5",
        "badge": "E8E9F7",
        "badge_cta": "5B5BD6",
        "badge_data": "DFE3F4",
        "typing": "#3D3D48",
    },
    "aurora": {
        "label": "极光",
        "desc": "青紫光晕 · 冷调",
        "bg": ("#FFFFFF", "#F2F6FD"),
        "wash": ["#DCF4F8", "#E6E4FB", "#DFF3EC"],
        "sub": "#41475A",
        "chips": ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
        "chip_text": "#363B4D",
        "accent": "#4C8DE8",
        "badge": "E2EAF8",
        "badge_cta": "3F62B8",
        "badge_data": "D8E1F4",
        "typing": "#363B4D",
    },
    "ocean": {
        "label": "海蓝",
        "desc": "蓝青光晕 · 通透",
        "bg": ("#FFFFFF", "#EFF7FB"),
        "wash": ["#D9EFFB", "#D7F3F6", "#E2ECFB"],
        "sub": "#3D4A55",
        "chips": ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
        "chip_text": "#33404B",
        "accent": "#2E9BC4",
        "badge": "DEEDF6",
        "badge_cta": "2C7FA8",
        "badge_data": "D3E6F2",
        "typing": "#33404B",
    },
    "sunset": {
        "label": "日落",
        "desc": "橙紫光晕 · 暖调",
        "bg": ("#FFFFFF", "#FBF4F0"),
        "wash": ["#FFE8DA", "#F0E2FA", "#FFE9F0"],
        "sub": "#55453F",
        "chips": ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
        "chip_text": "#4A3B35",
        "accent": "#E0763F",
        "badge": "F7E6DC",
        "badge_cta": "C45A2C",
        "badge_data": "F0DACA",
        "typing": "#4A3B35",
    },
    "candy": {
        "label": "糖果",
        "desc": "粉蓝光晕 · 明亮",
        "bg": ("#FFFFFF", "#FAF3F9"),
        "wash": ["#FFE4F1", "#E2ECFF", "#E6FBF2"],
        "sub": "#4A4352",
        "chips": ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
        "chip_text": "#403A48",
        "accent": "#C75BC8",
        "badge": "F2E4F4",
        "badge_cta": "A845A8",
        "badge_data": "E9D8EE",
        "typing": "#403A48",
    },
    "forest": {
        "label": "森野",
        "desc": "绿青光晕 · 沉稳",
        "bg": ("#FFFFFF", "#F1F8F4"),
        "wash": ["#DEF5E7", "#DAF2F0", "#E6F2DE"],
        "sub": "#3F4C44",
        "chips": ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
        "chip_text": "#37433B",
        "accent": "#3E9E76",
        "badge": "E0F1E8",
        "badge_cta": "2F805C",
        "badge_data": "D6EBE0",
        "typing": "#37433B",
    },
}

# 当前生效主题。改这一个值 = 换掉整套配色。
ACTIVE = "spectrum"

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


def rainbow_lut(n=1024):
    """彩虹查找表：长度 n，正好铺满一条完整光谱，末色接回首色。

    长度必须等于"流动周期"（也就是文字宽度），这样平移一整圈才接得上。
    早先把它做成文字宽度的两倍，结果只显示出半条光谱，紫色永远出不来。
    """
    stops = [hx(c) for c in RAINBOW] + [hx(RAINBOW[0])]
    seg = len(stops) - 1
    lut = []
    for i in range(n):
        t = (i / n) * seg
        k = min(int(t), seg - 1)
        f = t - k
        f = f * f * (3 - 2 * f)                    # smoothstep，避免色标处出现折角
        a, b = stops[k], stops[k + 1]
        lut.append(tuple(int(a[m] + (b[m] - a[m]) * f) for m in range(3)))
    return lut
