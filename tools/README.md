# 主题系统 —— 一套代码，六种白粉配色

主页所有视觉（banner、打字机、README 徽章、贡献卡）共用 `tools/theme.py` 里的配色定义。
**换主题只需要一条命令**，不会出现"改了 banner 忘了改徽章"的割裂。

## 设计前提

1. **白为主、粉做点缀** —— 整页约 75% 白，粉色只出现在 banner 渐变、徽章、
   强调线这些小面积地方。深色大面积铺底会显得闷、脏、很"AI"。
2. **不要金色** —— 橙色系（`#C98A3C` / `#FFAF70`）全部去掉。金色和粉色同时
   出现会互相打架，而且金色本身偏"商务模板感"。
3. **深色只出现在文字里** —— banner、标题、徽章底色一律是浅色或白色。
4. **名字用「深玫瑰 → 珊瑚粉」渐变** —— 在白底上既清晰又和整站粉色同源。

## 六套主题

| 名称 | 中文 | 底色 |
| :--- | :--- | :--- |
| `blush` | 胭脂 | 白 → 淡粉（当前） |
| `peony` | 牡丹 | 白 → 玫粉 |
| `sakura` | 樱 | 白 → 樱粉 |
| `lilac` | 紫藤 | 白 → 淡紫 |
| `cream` | 奶杏 | 白 → 奶杏 |
| `mint` | 薄荷 | 白 → 薄荷绿 |

## 切换主题

```powershell
D:\Anaconda3\python.exe tools\set_theme.py           # 列出全部
D:\Anaconda3\python.exe tools\set_theme.py sakura    # 切到樱
D:\Anaconda3\python.exe tools\set_theme.py all       # 重新生成全部六套
```

切主题会自动做四件事，**不需要手工改任何文件**：

1. 改 `tools/theme.py` 里的 `ACTIVE`
2. 把该主题的 `banner.svg` / `typing.gif` 复制到 `assets/` 根目录（README 引用的是这里）
3. 按主题重写 README 里所有 shields.io / komarev 徽章的颜色，以及 streak 卡片 URL
4. **bump README 里两张本地图的 `?v=N`**（camo 按 URL 缓存，不 bump 访客看不到新图）

改完照常 `git add -A; git commit; git push` 即可。

## 加一套自己的主题

在 `tools/theme.py` 的 `THEMES` 里加一项，照抄现有的改颜色即可，字段含义见文件顶部注释。
18 个徽章色必须两两不同（有断言挡着），改完跑 `set_theme.py all`。

---

## 生成器

```powershell
D:\Anaconda3\python.exe tools\set_theme.py all      # 一次生成全部主题
# 或单主题
D:\Anaconda3\python.exe tools\make_banner.py     blush
D:\Anaconda3\python.exe tools\make_typing_gif.py blush
D:\Anaconda3\python.exe tools\make_tech_icons.py     # 技术栈图标（与主题无关）
```

---

## 踩过的坑

### 1. ⚠️ 改完任何图都要 bump `?v=N`
GitHub 的 camo 按 URL 缓存。文件名和 URL 都没变 = 访客永远拿旧图。
`set_theme.py` 会帮你 bump，手改图时记得自己来。

### 2. ⚠️ 浅色渐变不能用 GIF
GIF 只有 256 色。深色底上的渐变勉强能糊过去，**白底上的渐变一定出色带**。
所以 banner 走 SVG（渐变绝对平滑、文字边缘锐利、文件还小几倍），
打字机只用平涂背景。动画只能交给 GIF——因为 SVG 里的 SMIL 在 GitHub 的
`<img>` 上下文不执行（实测 `<textPath>` 动画 `d` / `<clipPath>` 宽度 /
元素 opacity 轮播三种方案放进 GitHub 全空白，单独打开正常）。

### 3. ⚠️ shields.io 路径段徽章的颜色后面跟的是 `?` 不是 `&`
```
/badge/Python-A8485C?style=for-the-badge&logo=python
                      ↑ 0x3F      ↑ 这里才是 0x26
```
**两者 shields.io 都认，徽章显示完全正常、肉眼看不出任何问题** —— 但按 `&`
写替换逻辑的脚本会静默失效，16 枚徽章里有 11 枚换不掉。这就是换色"看起来不生效"的真正原因。
`set_theme.py` 用一条正则同时覆盖两种分隔符，并**逐色打印替换处数**。

### 4. ⚠️ 浅色底上的徽章文字颜色不用管
shields.io 会按背景亮度自动选黑或白文字。淡粉底（`#F8D7E1`）自动给深色文字 `#333`，
所以浅粉主题的徽章不需要任何额外处理——但要**查返回内容的体积**，
无效参数会返回 200 加一张约 256 字节的空图。

### 5. ⚠️ 打字机 GIF 用 `disposal=1` 就够，别上 `disposal=2`
`disposal=1`（不清屏）在"每帧整张重画"的写法下是正确的：删字时那些像素变回
背景色，属于实际变化，会被帧间差分正常记录。改成 `disposal=2` 也能正确显示，
但每帧都要整块存储，**体积从 92KB 涨到 647KB**。

> 这里踩了个更隐蔽的坑：一开始以为 `disposal=1` 会让字越叠越长，
> 是因为**取帧验证的索引算错了**（四次都落在第一句范围内），不是代码有问题。
> 为一个自己造出来的假 bug 付了 7 倍体积。**改之前先确认 bug 真的存在。**

### 6. ⚠️ GIF 的三个体积陷阱
- 逐帧独立 LZW 压缩、**不做帧间差分** → 静止元素每帧都要重压一遍
- 逐帧 `ADAPTIVE` 调色板会摧毁跨帧压缩 → 必须所有帧共用一套
- `FLOYDSTEINBERG` 抖动引入高频噪声 → 实测体积暴涨，必须 `dither=Image.NONE`

### 7. ⚠️ `.gitignore` 清理要彻底
曾给"被否决的实验"加过 `assets/banner-dark.gif` 规则，后来同名新文件一直没被提交，
线上 404 才发现。**淘汰资产时记得同步清规则。**
`tools/check_assets.py` 就是为这个写的。

---

## 提交前跑一遍校验

```powershell
D:\Anaconda3\python.exe tools\check_assets.py     # 本地图在不在 git 里 / ?v= 有没有分裂
D:\Anaconda3\python.exe tools\check_external.py   # 外部图 URL 是否还活着
```

`check_assets.py` 比"文件在不在磁盘上"严格一档：它拿 `git ls-files` 对，
也就是**真正提交上去的清单**。

`check_external.py` 除了状态码还看**体积**：shields.io 对无效参数会返回 200
加一张空图，光看状态码会误判成"正常"。它用 `urllib` 而不是 `subprocess curl`——
badge URL 里全是 `&`，在 PowerShell 里传给 `curl.exe` 会被拆成多个参数，
表现成"只回了 100 来字节"，极易误判成服务端故障。

---

## 本地预览页（已 gitignore）

- `preview/banner-preview.html` —— banner + 打字机，浅色/深色模式对比（改完刷新即可看）
- `preview/typing-frames.png` —— 打字机四句话各自打满的那一帧
- `preview/theme-sheet.png` —— 六套主题对比
- `preview/badge-palette.html` —— 徽章配色
