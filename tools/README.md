# 主题系统 —— 一套代码，六种彩虹配色

主页所有视觉（banner、打字机、README 徽章、贡献卡）共用 `tools/theme.py` 里的配色定义。
**换主题只需要一条命令**，不会出现"改了 banner 忘了改徽章"的割裂。

## 设计前提

1. **白底 + 淡彩光晕**。大面积保持白，背景只铺三团很淡的粉彩光晕。
   整页做成彩虹背景会俗气 —— 冲击力靠名字那一处就够了。
2. **彩虹只出现在会动的两个地方**：banner 名字的填充，和底部一条 4px 细线。
   胶囊描边也跟着流动，保持语言统一，但**不加新的运动**。
3. **不用粉色主导**。前一版白→淡粉被反馈"太娘炮"，所以每套主题的
   光晕和强调色必须**跨色相**（至少含暖 + 冷两个方向）。
4. **深色只出现在文字上**，不作为背景。

## 彩虹色带

```python
RAINBOW = ["#FF5C7A", "#FF9A3C", "#F7C948", "#5FD97E",
           "#35C4E4", "#5B7BF5", "#A96BEE"]
```

首尾同色，所以横向平移一整圈后能无缝接上。**六套主题共用这一条色带** ——
它是主页的签名，不随主题变；各主题的差异是背景光晕 `wash` 和强调色。

## 六套主题

| 名称 | 中文 | 光晕 |
| :--- | :--- | :--- |
| `spectrum` | 全彩 | 多色（全光谱）当前 |
| `aurora` | 极光 | 青紫 · 冷调 |
| `ocean` | 海蓝 | 蓝青 · 通透 |
| `sunset` | 日落 | 橙紫 · 暖调 |
| `candy` | 糖果 | 粉蓝 · 明亮 |
| `forest` | 森野 | 绿青 · 沉稳 |

## 切换主题

```powershell
D:\Anaconda3\python.exe tools\set_theme.py           # 列出全部
D:\Anaconda3\python.exe tools\set_theme.py sunset    # 切到日落
D:\Anaconda3\python.exe tools\set_theme.py all       # 重新生成全部六套
```

切主题会自动做四件事，**不需要手工改任何文件**：

1. 改 `tools/theme.py` 里的 `ACTIVE`
2. 把该主题的 `banner.gif` / `typing.gif` 复制到 `assets/` 根目录（README 引用的是这里）
3. 按主题重写 README 里所有 shields.io / komarev 徽章的颜色，以及 streak 卡片 URL
4. **bump README 里两张本地图的 `?v=N`**（camo 按 URL 缓存，不 bump 访客看不到新图）

改完照常 `git add -A; git commit; git push` 即可。

## 加一套自己的主题

在 `tools/theme.py` 的 `THEMES` 里加一项，照抄现有的改 `wash` / `accent` 即可。
18 个徽章色必须两两不同（有断言挡着），改完跑 `set_theme.py all`。

---

## 生成器

```powershell
D:\Anaconda3\python.exe tools\set_theme.py all      # 一次生成全部主题
# 或单主题
D:\Anaconda3\python.exe tools\make_banner_gif.py  spectrum
D:\Anaconda3\python.exe tools\make_typing_gif.py  spectrum
D:\Anaconda3\python.exe tools\make_tech_icons.py     # 技术栈图标（与主题无关）
```

---

## 踩过的坑

### 1. ⚠️ 彩虹渐变在 GIF 的 256 色下**不会**出色带
一开始以为会：GIF 量化必然产生色带，白底上尤其明显。
**实测不会。** 色带是低彩度窄范围渐变（白→粉）的问题；彩虹色相跨度大，
色相本身就是调色板里最省的部分。24 帧无可见色带、无接缝。

### 2. ⚠️ ramp 长度必须等于"流动周期"
把 ramp 做成文字宽度的两倍、取滑动窗口，结果**只显示出半条光谱**，紫色永远出不来，
而且看着像"渐变没画完"。ramp 长度 = 文字宽度，按该周期取模回绕才对。

### 3. ⚠️ `disposal=1` vs `disposal=2` 在这里差 5 倍体积
背景、光晕、副标题、胶囊底每帧都一样，只有名字/细线/描边/底条在变。
用 `disposal=2`（强制整帧存储）体积 437KB；改回 `displacement=1`
让帧间差分吃掉静态部分，**90KB**。

> 配套教训：上一轮我为**一个不存在��� bug** 把 `disposal` 改了。
> 真正的原因是我取帧验证的索引算错了（四次都落在第一句范围内），
> 不是代码有问题。**改之前先确认 bug 真的存在。**

### 4. ⚠️ 渐变要用 numpy 建，不能逐像素填
1000×270 每帧 27 万个点、18 帧就是 480 万次 Python 循环，慢到不可用。
`np.repeat` 一次搞定，几十毫秒。

### 5. ⚠️ `np.asarray(PIL图)` 是只读的
写 alpha 通道会报 `assignment destination is read-only`。要改就用 `np.array(...)`。

### 6. ⚠️ 改完任何图都要 bump `?v=N`
GitHub 的 camo 按 URL 缓存。文件名和 URL 都没变 = 访客永远拿旧图。

### 7. ⚠️ shields.io 路径段徽章的颜色后面跟的是 `?` 不是 `&`
```
/badge/Python-A8485C?style=for-the-badge&logo=python
                      ↑ 0x3F      ↑ 这里才是 0x26
```
**两者 shields.io 都认，显示完全正常、肉眼看不出问题** —— 但按 `&`
写替换逻辑的脚本会静默失效。所以 `set_theme.py` 里的匹配写成
`r"(-|(?:labelColor|color)=)"`：路径段是 `-颜色`，查询串是 `color=`，
而 **`labelColor` 的 C 是大写**，只写 `color=` 会漏掉它。

### 8. ⚠️ 浅色底上的徽章文字颜色不用管
shields.io 按背景亮度自动选黑或白文字。淡紫底（`#E8E9F7`）自动给深色文字。
但要**查返回内容的体积**——无效参数会返回 200 加一张约 256 字节的空图。

### 9. ⚠️ streak 卡片有两个坑
- 中间那列的 "Current Streak" 文字是对方**硬编码的 `#FB8C00`（橙金）**，
  不传 `currStreakLabel` 改不掉。
- 卡片背景不能给纯白：GitHub 默认白色页面上，纯白卡片等于隐形。用 `bg[1]`。

**验证自定义配色不能只看"渲染出来了"，要 grep 返回的 SVG 里还有没有你不想要的颜色值。**

### 10. ⚠️ `.gitignore` 清理要彻底
曾给"被否决的实验"加过 `assets/banner-dark.gif` 规则，后来同名新文件一直没被提交，
线上 404 才发现。`tools/check_assets.py` 就是为这个写的。

---

## 提交前跑一遍校验

```powershell
D:\Anaconda3\python.exe tools\check_assets.py     # 本地图在不在 git 里 / ?v= 有没有分裂
D:\Anaconda3\python.exe tools\check_external.py   # 外部图 URL 是否还活着
```

`check_assets.py` 拿 `git ls-files`（真正提交上去的清单）对，不是看磁盘上有没有。

`check_external.py` 除了状态码还看**体积**。它用 `urllib` 而不是 `subprocess curl`——
badge URL 里全是 `&`，在 PowerShell 里传给 `curl.exe` 会被拆成多个参数，
表现成"只回了 100 来字节"，极易误判成服务端故障。

---

## 本地预览页（已 gitignore）

- `preview/themes.html` —— 六套主题 × 浅色/深色模式的首屏对比
- `preview/banner-rainbow.png` —— banner 三个相位的静帧拼接
- `preview/typing-frames.png` —— 打字机四句话各自打满的那一帧
