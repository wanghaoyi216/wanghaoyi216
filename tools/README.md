# 主页视觉资产流水线

这个仓库的 README 里有 5 张自制图片，它们不是一次做出来的，而是由 `tools/` 下的脚本生成。
**要改配色、换字体、加技术栈、换文案，请改脚本后重跑，不要直接手改 `assets/` 里的成品文件**——
下次重跑会把手改覆盖掉。

## 一条命令全量重建

```powershell
D:\Anaconda3\python.exe tools\make_banner.py        # banner（深色，名字排版）
D:\Anaconda3\python.exe tools\make_tech_icons.py   # 技术栈三行图标
D:\Anaconda3\python.exe tools\make_typing_gif.py   # 打字机 GIF
git add -A; git commit -m "..."; git push
```

---

## 一、名字排版：为什么改成这样

**原来的写法（全大写 + 均匀字距 + 无衬线）是最典型的"板正"排版**，
反馈是"太板正、要有艺术感、大字小字搭配"。

现在的方案（B 方案，从五个候选里选出）：

| 元素 | 字体 | 字号 | 作用 |
| :--- | :--- | :--- | :--- |
| `Haoyi` | Bodoni MT **Italic** | 92 | 主视觉，巨大衬线斜体 |
| `Wang` | **Segoe Script** | 52 | 手写体，垂直错落 6px 形成层次 |
| 副标题 | Bodoni MT | 17（手动字距 3.4） | 宽字距衬线，压住下方 |
| 三个标签 | 微软雅黑 | 13 | 信息胶囊 |

去掉"板正感"的三个关键动作：
1. **全大写 → 混合大小写**（最快见效的一步）
2. **单一字号 → 大小两级对比**（92 vs 52）
3. **同一字体 → 衬线 + 手写混搭**（有对比才有性格）

### ⚠️ 必须知道：文字是转成路径的，不是 `<text>`

`make_banner.py` 用 **fontTools 的 SVGPathPen 把所有文字转成矢量路径**再嵌进 SVG。
生成的文件里 **没有任何 `<text>` 元素、没有任何 `font-family`**。

**原因**：Bodoni MT 和 Segoe Script 只在 Windows 上装了。
如果 SVG 里只写 `font-family="Bodoni MT"`，Mac / Linux 访客会掉成默认衬线体，排版直接崩。

对比成本：

| 做法 | 体积 | 跨系统一致性 |
| :--- | :--- | :--- |
| `<text>` + `font-family` | 79 KB | ❌ Mac/Linux 排版崩 |
| `@font-face` 内嵌 base64 | 约 900 KB | ✅ |
| **转成路径（当前做法）** | **108 KB** | ✅ |

**代价**：改文字必须改脚本重跑，不能在 Figma 之类的工具里直接编辑。

换字体的话改 `make_banner.py` 顶部的常量：
```python
SERIF_I = Bodoni MT Italic   ->  首名
SCRIPT  = Segoe Script       ->  姓氏
SERIF_R = Bodoni MT          ->  副标题
CJK     = 微软雅黑            ->  中文标签
```

---

## 二、三条踩过的坑

### 1. ⚠️ 改完必须给 README 里的图片 URL 加版本号

```markdown
<img src="./assets/banner-dark.svg?v=6">
```

**GitHub 的 camo 代理按 URL 缓存。** 文件名没变、URL 没变，访客拿到的还是旧图。
每次重新生成资产后把 `?v=N` 的 N 加一，否则你的修改不会生效（会白等很久）。

### 2. ⚠️ README 里不要依赖 SVG 动画

Chrome 在把 SVG 当 `<img>` 渲染时（GitHub README 就是这种场景）**不执行 SMIL 动画**。
实测：`readme-typing-svg` 的打字机、自制的 `<clipPath>` 宽度动画、元素 opacity 轮播，
放进 GitHub 全部变成空白；单独打开 SVG 却一切正常。

**所以：需要动的地方一律用 GIF。** GIF 在 `<img>` 里一定动。

对应的设计约束：**任何元素在「动画不跑」的静态状态下都必须好看**。
banner 里所有元素都满足这一条，所以它虽然不动画也依然好看——这是当初这么设计的原因。

### 3. ⚠️ 只做深色版，不要做浅色版

浅色 banner / 浅色打字机已经**全部删除**。

原因：浅色版本身发灰、和下方内容衔接生硬。为了凑"双主题"硬做一套更差的设计，
反而拉低了整体观感。顶级主页普遍是 **hero 恒定深色**，不论访客用的是什么主题。
`README.md` 里也去掉了 `<picture>`，直接用单一 `<img>`。

---

## 三、两个已被否决的实验（别再走一遍）

### `make_banner_gif.py` —— banner 动图，已否决

2026-09-29 同尺寸 A/B 实测：

| | SVG（108 KB） | GIF（428 KB） |
| :--- | :--- | :--- |
| 文字 | 矢量锐利 | 发软 |
| 等高线 | 细腻 | 偏粗 |
| 观感 | 精致 | 业余 |

428 KB 只换来「等高线缓慢旋转」这一处微弱动效，不划算。**页面的动感交给打字机 GIF 就够了。**

> 附带记录几条 GIF 体积知识（做别的动图时会用到）：
> - GIF 逐帧独立 LZW 压缩，**不做帧间差分** → 静止背景在每帧都要重压一遍，减帧数是唯一有效杠杆
> - 逐帧 `ADAPTIVE` 调色板会摧毁跨帧压缩，必须所有帧共用一套调色板
> - `FLOYDSTEINBERG` 抖动引入高频噪声，实测让体积从 428 KB 涨到 1475 KB

### `make_typo_sheet.py` —— 排版候选样张

保留着。改名字排版时跑一下，能一次看到 5 种方案的实际效果（背景和线上 banner 一致），
比单独看字体样本靠谱得多。用户在 A–E 五个方案里选了 B。

---

## 四、其他脚本

### `make_tech_icons.py` —— 技术栈三行图标

从 `assets/tech/*.svg`（simple-icons）合成 `assets/tech-{languages,frameworks,data}.svg`。
**品牌配色由本脚本指定**，比 skillicons.dev 固定深色好看，而且不依赖任何第三方服务。

改技术栈：编辑 `ROWS` 字典 → 把对应 svg 放进 `assets/tech/` → 重跑。

常用 slug：`py java ts js html5 css vuedotjs spring react docker git github mysql
postgresql redis mongodb apachekafka nginx linux`

> ⚠️ slug 大小写敏感。`vuedotjs` 和 `vue` 只有一个有效（用 `vue`）。
> 取不到就是 slug 不存在：`https://cdn.simpleicons.org/<slug>`。

### `make_typing_gif.py` —— 打字机动画

生成 `assets/typing-dark.gif`，中英三行逐字打字 + 光标。**只做深色版。**

改文案：编辑 `LINES`。
调节奏：`TYPE_F`（打字占比）/ `HOLD_F`（停留）/ `ERASE_F`（擦除），三者加起来是 1。

> ⚠️ 颜色写 `"#58A6FF"` 字符串，脚本内部用 `ImageColor.getrgb` 转元组。
> 直接传元组会报 `TypeError: can only concatenate str (not "tuple") to str`。

---

## 五、改完之后

1. **push 之后硬刷新**（Ctrl+F5）。camo 缓存 + 浏览器缓存都要绕。
2. 看一眼 https://github.com/wanghaoyi216 确认没有裂图、构图没跑偏。
3. 本地校验页（已 gitignore，不在公开仓库里）：
   - `preview/theme-check.html` —— 深浅主题模拟
   - `preview/banner-ab.html` —— banner 各版本 A/B
   - `preview/typography-sheet.png` —— 名字排版候选
