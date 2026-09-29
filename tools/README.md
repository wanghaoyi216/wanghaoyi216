# 主页视觉资产流水线

这个仓库的 README 里有 5 张自制图片，由 `tools/` 下的脚本生成。
**要改配色、换字体、换文案，请改脚本后重跑，不要直接手改 `assets/` 里的成品文件**。

## 全量重建

```powershell
D:\Anaconda3\python.exe tools\make_banner_gif.py   # banner（流动波浪渐变名字）
D:\Anaconda3\python.exe tools\make_tech_icons.py  # 技术栈三行图标
D:\Anaconda3\python.exe tools\make_typing_gif.py  # 打字机 GIF
git add -A; git commit -m "..."; git push
```

⚠️ **推完记得改 README 里的 `?v=N`**（见坑 1），否则访客看到的还是旧图。

---

## 一、两个 GIF 的字体与效果

| 资产 | 中文 | 英文 | 效果 |
| :--- | :--- | :--- | :--- |
| `banner-dark.gif` | — | — | 名字是**流动 + 波浪形渐变** |
| `typing-dark.gif` | **华文行楷** `STXINGKA.TTF` | **Comic Sans MS** `comic.ttf` | 逐字打字 + 光标 |

**banner 名字的波浪渐变怎么算的**（`make_banner_gif.py` 的 `wave_field()`）：

```
t = frac( x/W + phase )  +  amp * sin( 2π·y/H·freq + phase·2.4 )
```
- `x/W + phase` → 水平随时间平移 = **流动**
- `amp·sin(...)` → 垂直正弦起伏 = **波浪形**

然后用一条 5 段色带（深青 → 亮青 → 近白 → 亮青 → 深青）把 `t` 映射成颜色，
再用文字遮罩把它裁出来。`phase` 逐帧递增就是动画。

想调手感改这几个量：
- 流动更快 → 减小 `duration`（默认 140ms/帧）或增大 `FRAMES`
- 波浪更明显 → 调大 `amp`（默认 0.085）、`freq`（默认 1.6）
- 颜色换风格 → 改 `RAMP`

---

## 二、四条踩过的坑

### 1. ⚠️ 改完必须给 README 里的图片 URL 加版本号

```markdown
<img src="./assets/banner-dark.gif?v=8">
```

**GitHub 的 camo 代理按 URL 缓存。** 文件名没变、URL 没变，访客拿到的还是旧图。
每次重新生成资产后把 `?v=N` 的 N 加一。

### 2. ⚠️ README 里不要依赖 SVG 动画

Chrome 在把 SVG 当 `<img>` 渲染时（GitHub README 就是这种场景）**不执行 SMIL 动画**。
实测三种方案（`<textPath>` 动画 `d` / `<clipPath>` 宽度 / 元素 opacity 轮播）
放进 GitHub 全部空白，单独打开却正常。

**所以：会动的一律用 GIF。** 这也是 banner 从 SVG 改成 GIF 的原因 ——
用户要求名字有"流动"效果，SVG 做不到。

> 代价：GIF 只有 256 色且逐帧独立压缩，文字比矢量 SVG 稍软。
> 在 banner 这个尺寸下（1000×250 显示约 890px）差异不明显，动画收益远大于这点损失。

### 3. ⚠️ 只做深色版

浅色 banner / 浅色打字机已全部删除。浅色版本身发灰、且和下方内容衔接生硬；
顶级主页普遍是 **hero 恒定深色**，不论访客用什么主题。README 里也没有 `<picture>`。

### 4. ⚠️ GIF 的三个体积陷阱

- **逐帧独立 LZW 压缩，不做帧间差分** → 静止背景每帧都要重压一遍，**减帧数是唯一有效杠杆**
- **逐帧 `ADAPTIVE` 调色板会摧毁跨帧压缩** → 必须所有帧共用一套（代码里把 2 帧拼起来建一次调色板）
- **`FLOYDSTEINBERG` 抖动引入高频噪声** → 实测让体积从 428 KB 涨到 1475 KB，必须 `dither=Image.NONE`

当前体积：banner 554 KB + typing 59 KB。

---

## 三、已被淘汰的东西

| 文件 | 状态 |
| :--- | :--- |
| `assets/banner-dark.svg` | 已淘汰（SVG 不支持 GitHub 动画），已加入 .gitignore |
| `assets/banner-light.svg` / `typing-light.gif` | 已删除（浅色主题方案废弃） |
| `make_banner.py`（SVG 版） | 保留但**当前不使用**。它包含 fontTools 转路径的实现，浅色版方案若复活会用得上 |

### `make_typo_sheet.py` —— 排版候选样张

保留着。改名字排版时跑一次，能一次看到 5 种方案在**真实 banner 背景**下的效果，
比单看字体样本靠谱得多。用户在 A–E 五个方案里选了 B（巨大衬线首名 + 手写姓氏）。

---

## 四、`make_tech_icons.py`

从 `assets/tech/*.svg`（simple-icons）合成三行品牌配色图标。
比 skillicons.dev 固定深色好看，而且不依赖任何第三方服务（skillicons.dev 实测不稳定）。

改技术栈：编辑 `ROWS` → 把对应 svg 放进 `assets/tech/` → 重跑。

常用 slug：`py java ts js html5 css vuedotjs spring react docker git github mysql
postgresql redis mongodb apachekafka nginx linux`

> ⚠️ slug 大小写敏感，`vuedotjs` 和 `vue` 只有一个有效（用 `vue`）。
> 取不到就说明 slug 不存在：`https://cdn.simpleicons.org/<slug>`

---

## 五、徽章配色是统一的，别改回品牌色

所有徽章都用同一个海洋蓝 `#0B5C7A`（数据徽章用更深的 `#0E3A4A` 退到次要层）。

**不要改回各技术栈的品牌原色**（Vue 亮绿 / Java 亮橙 / Docker 亮红）——
那一排彩虹和克制的 banner 风格打架，是之前"看起来很丑"的主要原因之一。
`preview/badge-palette.html` 里有三种方案的对比。

---

## 六、改完之后

1. **硬刷新**（Ctrl+F5）。camo 缓存 + 浏览器缓存都要绕。
2. 看一眼 <https://github.com/wanghaoyi216>，确认没有裂图、构图没跑偏。
3. 本地校验页（已 gitignore）：
   - `preview/badge-palette.html` —— 徽章配色三方案
   - `preview/typography-sheet.png` —— 名字排版五方案
   - `preview/typing-check.html` —— banner + 打字机整体气质
