# 主页视觉资产流水线

全部图片由 `tools/` 下的脚本生成，**不要直接手改 `assets/` 里的成品**（下次重跑会覆盖）。

```powershell
D:\Anaconda3\python.exe tools\make_banner_gif.py   # banner（暖色 + 星光 + 波浪渐变名字）
D:\Anaconda3\python.exe tools\make_typing_gif.py   # 打字机
D:\Anaconda3\python.exe tools\make_divider.py     # 分隔线
D:\Anaconda3\python.exe tools\make_tech_icons.py  # 技术栈图标
```

⚠️ 改完任何一张图，**把 README 里对应 URL 的 `?v=N` 加一**。GitHub 的 camo 按 URL 缓存，
不 bump 版本号的话，访客（包括你自己）看到的还是旧图。

---

## 一、视觉系统

| | 取值 |
| :--- | :--- |
| 底色 | 深紫红 `#1A0F21` → 暖酒红 `#4E2830` |
| 名字色带 | 桃红 `#FF8A8F` → 近白暖高光 → 橙金 `#FFC56C` → 深橘 `#F28A3A` |
| 徽章主色 | 玫瑰 `#A8485C`（CTA 用金 `#C98A3C`，数据徽章用暗酒红 `#6B3A3F`） |

**徽章不要改回各技术栈的品牌原色**（Vue 亮绿 / Java 亮橙 / Docker 亮红）——
一排彩虹会和暖色 banner 打架，是之前"看起来很丑 / AI 感重"的主要原因之一。
对比见 `preview/badge-palette.html`。

---

## 二、三个 GIF

| 资产 | 中文 | 英文 | 效果 |
| :--- | :--- | :--- | :--- |
| `banner-dark.gif` | — | — | 名字 = 流动 + 波浪渐变，满屏星光闪烁 |
| `typing-dark.gif` | **华文行楷** | **Comic Sans MS Bold** | 逐字打字 + 光标，负字距制造连笔感 |
| `divider.svg` | — | — | 静态分隔线，暖色渐变 + 星光 |

### banner 的波浪渐变怎么算

```
t = frac( x/W + phase ) + amp·sin( 2π·y/H·freq + phase·2.4 )
```
- `x/W + phase` → 水平平移 = **流动**
- `amp·sin(...)` → 垂直正弦 = **波浪形**

**`freq` 必须高到"文字高度内至少跑完一个周期"**，否则出来只是斜向渐变、不是波浪。
文字高约 55px、画布 250px，所以 `freq ≈ 4.5`（当前用 4.0）。
`amp` 再大会明暗不均，0.10~0.13 之间最平衡。对比见 `preview/wave-compare2.png`。

---

## 三、踩过的坑

### 1. ⚠️ 改完必须 bump `?v=N`
camo 按 URL 缓存，同名同 URL 永远拿旧图。

### 2. ⚠️ GitHub 的 `<img>` 里 SVG 动画不执行
Chrome 在把 SVG 当 `<img>` 渲染时不跑 SMIL。实测三种方案（`<textPath>` 动画 `d` /
`<clipPath>` 宽度 / 元素 opacity 轮播）放进 GitHub 全空白，单独打开却正常。
**会动的一律用 GIF。** 这也是 banner 从 SVG 改成 GIF 的原因。

### 3. ⚠️ GIF 的三个体积陷阱
- 逐帧独立 LZW 压缩、**不做帧间差分** → 静止元素每帧都要重压一遍，**减帧数是唯一有效杠杆**
- 逐帧 `ADAPTIVE` 调色板会摧毁跨帧压缩 → 必须所有帧共用一套
- `FLOYDSTEINBERG` 抖动引入高频噪声 → 实测体积从 428KB 涨到 1475KB，必须 `dither=Image.NONE`

**实测：banner 里那层 40px 间距的"地图网格线"几乎看不见（32/255 透明度），
却让文件从 385KB 涨到 554KB。细密线条是 GIF 压缩的天敌，已删除。**

### 4. ⚠️ `.gitignore` 清理要彻底
曾经给"被否决的实验"加过 `assets/banner-dark.gif` 规则，后来同名新文件一直没被提交，
线上 404 才发现。**淘汰资产时记得同步清规则。**

---

## 四、已淘汰

| 文件 | 状态 |
| :--- | --- |
| `assets/banner-dark.svg` | 已淘汰（SVG 不支持 GitHub 动画） |
| `assets/banner-light.svg` / `typing-light.gif` | 已删除（浅色主题方案废弃） |
| `make_banner.py`（SVG 版） | 保留但不使用，含 fontTools 转路径实现 |
| `make_style_sheet.py` | 保留，生成 A/B/C 三种风格样张供选型 |

## 五、本地校验页（已 gitignore）

- `preview/style-sheet.png` —— A/B/C 三种 banner 方向
- `preview/wave-compare2.png` —— 波浪参数四档
- `preview/badge-palette.html` —— 徽章配色三方案
- `preview/typography-sheet.png` —— 名字字体五方案
