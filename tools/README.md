# 主题系统 —— 一套代码，六种配色

主页所有视觉（banner、打字机、分隔线、README 徽章）共用 `tools/theme.py` 里的配色定义。
**换主题只需要一条命令**，不会出现"改了 banner 忘了改徽章"的割裂。

## 六套主题

| 名称 | 中文 | 名字色带 |
| :--- | :--- | :--- |
| `warm` | 暖阳 | 桃红 → 橙金（当前） |
| `aurora` | 极光 | 薄荷 → 冰蓝 |
| `sakura` | 樱粉 | 樱粉 → 淡紫 |
| `nebula` | 星海 | 靛蓝 → 洋红 |
| `mint` | 薄荷 | 薄荷绿 → 青柠 |
| `noir` | 墨金 | 哑光金（黑底，高雅路线） |

对比图见 `preview/theme-sheet.png`。

## 切换主题

```powershell
D:\Anaconda3\python.exe tools\set_theme.py           # 列出全部
D:\Anaconda3\python.exe tools\set_theme.py sakura    # 切到樱粉
D:\Anaconda3\python.exe tools\set_theme.py all       # 重新生成全部六套
```

切主题会自动做四件事，**不需要手工改任何文件**：

1. 改 `tools/theme.py` 里的 `ACTIVE`
2. 把该主题的 `banner.gif` / `typing.gif` / `divider.svg` 复制到 `assets/` 根目录
3. 按主题重写 `README.md` 里所有 shields.io / komarev 徽章的颜色
4. **bump README 里本地图的 `?v=N`**（camo 按 URL 缓存，不 bump 访客看不到新图）

改完照常 `git add -A; git commit; git push` 即可。

## 加一套自己的主题

在 `tools/theme.py` 的 `THEMES` 里加一项，照抄现有的改颜色即可，字段含义见文件顶部注释。
加完跑 `set_theme.py all` 就有了。

---

## 生成器

```powershell
D:\Anaconda3\python.exe tools\set_theme.py all     # 一次生成全部主题
# 或单主题
D:\Anaconda3\python.exe tools\make_banner_gif.py sakura
D:\Anaconda3\python.exe tools\make_typing_gif.py sakura
D:\Anaconda3\python.exe tools\make_divider.py   sakura
D:\Anaconda3\python.exe tools\make_tech_icons.py      # 技术栈图标（与主题无关）
```

---

## 波浪渐变算法

名字的「流动 + 波浪」是一个解析式，不是画出来的：

```
t = frac( x/W + phase ) + amp·sin( 2π·y/H·freq + phase·2.4 )
```
- `x/W + phase` → 水平随时间平移 = **流动**
- `amp·sin(...)` → 垂直正弦起伏 = **波浪形**

**`freq` 必须高到「文字高度内至少跑完一个周期」**，否则出来只是斜向渐变、不是波浪。
文字高约 55px、画布 250px，所以要 `freq ≈ 4.5`（当前 4.0）。`amp` 再大会明暗不均。

对比见 `preview/wave-compare2.png`。

---

## 踩过的坑

### 1. ⚠️ 改完任何图都要 bump `?v=N`
GitHub 的 camo 按 URL 缓存。文件名和 URL 都没变 = 访客永远拿旧图。
`set_theme.py` 会帮你 bump，手改图时记得自己来。

### 2. ⚠️ GitHub 的 `<img>` 里 SVG 动画不执行
Chrome 把 SVG 当 `<img>` 渲染时不跑 SMIL。实测三种方案（`<textPath>` 动画 `d` /
`<clipPath>` 宽度 / 元素 opacity 轮播）放进 GitHub 全空白，单独打开却正常。
**会动的一律用 GIF。** 分隔线是静态的，所以用 SVG。

### 3. ⚠️ GIF 的三个体积陷阱
- 逐帧独立 LZW 压缩、**不做帧间差分** → 静止元素每帧都要重压一遍，**减帧数是唯一有效杠杆**
- 逐帧 `ADAPTIVE` 调色板会摧毁跨帧压缩 → 必须所有帧共用一套
- `FLOYDSTEINBERG` 抖动引入高频噪声 → 实测 428KB 涨到 1475KB，必须 `dither=Image.NONE`

**实测：banner 里那层 40px 间距的地图网格线几乎看不见（32/255 透明度），
却让文件从 385KB 涨到 554KB。细密线条是 GIF 压缩的天敌，已删除。**

### 4. ⚠️ `.gitignore` 清理要彻底
曾给"被否决的实验"加过 `assets/banner-dark.gif` 规则，后来同名新文件一直没被提交，
线上 404 才发现。**淘汰资产时记得同步清规则。**

### 5. ⚠️ shields.io 路径段徽章的颜色后面跟的是 `?` 不是 `&`
```
/badge/Python-A8485C?style=for-the-badge&logo=python
                      ↑ 0x3F      ↑ 这里才是 0x26
```
路径段式（`/badge/名字-颜色`）的颜色和查询串之间用的是 `?`，查询参数式
（`?label=Stars&color=6B3A3F&style=`）才用 `&`。

**两者 shields.io 都认，徽章显示完全正常，肉眼看不出任何问题** —— 但按 `&` 写替换
逻辑的脚本会静默失效，16 枚徽章里有 11 枚换不掉。这就是换色"看起来不生效"的真正原因。

**判据：换色脚本必须打印替换处数，全 0 就是没换成功，别把"没报错"当成"成功"。**
`set_theme.py` 现在会逐色打印 `A8485C -> 17786A  9 处`，并���换完后扫一遍 README，
只要还有别的主题色残留就直接抛错、不写文件。

---

## 本地校验页（已 gitignore）

- `preview/theme-sheet.png` —— 六套主题对比
- `preview/style-sheet.png` —— A/B/C 三种风格方向
- `preview/wave-compare2.png` —— 波浪参数四档
- `preview/badge-palette.html` —— 徽章配色三方案
- `preview/typography-sheet.png` —— 名字字体五方案
