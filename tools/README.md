# 主页视觉资产流水线

这个仓库的 README 里有 7 张自制图片，它们不是一次做出来的，而是由 `tools/` 下的脚本生成。
**要改配色、加技术栈、换文案，请改脚本后重跑，不要直接手改 `assets/` 里的成品文件**——
下次重跑会把手改覆盖掉。

## 一条命令全量重建

```powershell
D:\Anaconda3\python.exe tools\make_banner.py        # banner（深/浅）
D:\Anaconda3\python.exe tools\make_tech_icons.py   # 技术栈三行图标
D:\Anaconda3\python.exe tools\make_typing_gif.py   # 打字机 GIF（深/浅）
git add -A; git commit -m "..."; git push
```

---

## 各脚本说明

### `make_banner.py` —— 顶部 banner

生成 `assets/banner-{dark,light}.svg`。用多谐波函数画等高线（`r(θ) = r₀·(1 + a₁sin3θ + a₂sin5θ + a₃sin8θ)`），
所以线条是自然的山脊状而不是规则圆。

| 想改什么 | 改哪里 |
| :--- | :--- |
| 配色 | `build()` 开头的 `bg1/bg2/bg3`、`line`、`title`、`sub` |
| 名字 / 副标题 | `build()` 里的 `<text>` 那一段 |
| 三个标签胶囊 | `labels = [...]`（**宽度会自动按中英文分别算**，别手填 `widths`） |
| 等高线疏密 | `topo_paths()` 的 `wobble` 三个系数 |
| 浅色版对比度 | `cboost` / `gboost`（浅色底需要更大才看得清） |

> ⚠️ 用 `-` 开头或结尾的胶囊宽度一定要用 `text_w()` 算，直接写数字会文字溢出重叠（踩过）。

### `make_tech_icons.py` —— 技术栈三行图标

从 `assets/tech/*.svg`（simple-icons）合成 `assets/tech-{languages,frameworks,data}.svg`。
图标的**品牌配色由本脚本指定**，比 skillicons.dev 固定深色好看，而且不依赖任何第三方服务。

改技术栈：编辑 `ROWS` 字典，加图标名 → 把对应的 svg 放进 `assets/tech/` → 重跑。

常用 slug：`py java ts js html5 css vuedotjs spring react docker git github mysql
postgresql redis mongodb apachekafka nginx linux`

> ⚠️ slug 大小写敏感。`vuedotjs` 和 `vue` 只有一个有效（用 `vue`）。
> 图标下下来是 `cdn.simpleicons.org/<slug>`，取不到就是 slug 不存在。

### `make_typing_gif.py` —— 打字机动画

生成 `assets/typing-{dark,light}.gif`，中英三行逐字打字 + 光标。

改文案：编辑 `LINES`。
调节奏：`TYPE_F`（打字占比）/ `HOLD_F`（停留）/ `ERASE_F`（擦除），三者加起来是 1。

> ⚠️ 颜色要写成 `"#58A6FF"` 字符串，脚本内部用 `ImageColor.getrgb` 转元组。
> 直接传元组会报 `TypeError: can only concatenate str (not "tuple") to str`。

---

## 三条踩过的坑（改之前务必先看）

### 1. ⚠️ 改完必须给 README 里的图片 URL 加版本号

```markdown
<img src="./assets/banner-dark.svg?v=5">
```

**GitHub 的 camo 代理按 URL 缓存。** 文件名没变、URL 没变，访客拿到的还是旧图。
每次重新生成资产后，把 `?v=N` 的 N 加一，否则你的修改不会生效（会白等很久）。

### 2. ⚠️ README 里不要依赖 SVG 动画

Chrome 在把 SVG 当 `<img>` 渲染时（GitHub README 就是这种场景）**不执行 SMIL 动画**。
实测：`readme-typing-svg` 的打字机、自制的 `<clipPath>` 宽度动画、元素 opacity 轮播，
放进 GitHub 全部变成空白；单独打开 SVG 却一切正常。

**所以：需要动的地方一律用 GIF。** GIF 在 `<img>` 里一定动。

对应的设计约束：**任何元素在「动画不跑」的静态状态下都必须好看**。
banner 里所有元素都满足这一条，所以它虽然不动画也依然好看——这是当初这么设计的原因。

### 3. ⚠️ 不要再把 banner 换成 GIF

`make_banner_gif.py` 是一次**已被否决**的实验，生成结果不在仓库里（已 gitignore）。
2026-09-29 同尺寸 A/B 实测结论：

| | SVG（79 KB） | GIF（428 KB） |
| :--- | :--- | :--- |
| 文字 | 矢量锐利 | 发软 |
| 等高线 | 细腻 | 偏粗 |
| 观感 | 精致 | 业余 |

428 KB 只换来「等高线缓慢旋转」这一处微弱动效，不划算。**页面的动感交给打字机 GIF 就够了。**

> 附带记录几条 GIF 体积知识（做别的动图时会用到）：
> - GIF 逐帧独立 LZW 压缩，**不做帧间差分** → 静止背景在每帧都要重压一遍，减帧数是唯一有效杠杆
> - 逐帧 `ADAPTIVE` 调色板会摧毁跨帧压缩，必须所有帧共用一套调色板
> - `FLOYDSTEINBERG` 抖动引入高频噪声，实测让体积从 428 KB 涨到 1475 KB

---

## 改完之后

跑一次体检，确认没有裂图：

```powershell
# 检查 README 里所有图片是否可访问
D:\Anaconda3\python.exe -c "..."
```

或者直接打开 <https://github.com/wanghaoyi216> 看一眼。深浅两种主题都要看
（浏览器跟随系统主题，只看一种容易漏问题——浅色版曾经就有等高线太淡、底部杂条两个缺陷）。

本地还有两个校验页（已 gitignore，不在公开仓库里）：

- `preview/theme-check.html` —— 深浅双主题模拟
- `preview/banner-ab.html` —— banner 各版本 A/B 对比
