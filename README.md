# Typora VitePress Theme

让 Typora 拥有 [VitePress](https://vitepress.dev) 默认文档站点的排版与配色。

主题直接复用了 VitePress 自己的 CSS 变量命名（`--vp-*`），因此任何熟悉 VitePress 定制方式的人，可以用完全相同的思路来改这个主题。

- 参考基准：`vitepress@1.6.4`（`src/client/theme-default/styles/`）
- 纯 CSS 主题：复制进主题文件夹即可，不需要插件、不需要装字体（每份约 5.2 MB，见下）
- **不需要安装任何字体**：`Ioskeley Mono` 与 `Sarasa Mono J` 都以 base64 WOFF2 内嵌在 CSS 里
- 通过 `prefers-color-scheme` 自动跟随系统切换 **浅色 / 深色**，不需要额外的深色主题文件
- 正文字号全部使用 `rem`，Typora 的「字体大小」偏好设置依然生效
- 正文列宽两种：**normal**（980px 阅读栏，默认）与 **fullwidth**（铺满窗口），在 **主题** 菜单里二选一

## 安装

1. 打开 Typora → 偏好设置 → 外观 → **打开主题文件夹**
2. 把 `typora-vitepress.css` 复制进去；想要 fullwidth 就再把 `typora-vitepress-fullwidth.css` 一起复制
3. 重启 Typora，在 **主题** 菜单里选择 `typora-vitepress`（normal）或 `typora-vitepress-fullwidth`（fullwidth）

> 两个 CSS 每个都有 5 MB 出头，因为它们各背了一份内联字体；复制/首次加载会稍慢一点点，之后没有区别。
> fullwidth 那份是脚本生成的，不要手改（见「自定义 → 列宽」）。

> macOS 上主题文件夹通常是 `~/Library/Application Support/abnerworks.Typora/themes/`。

## 还原了哪些 VitePress 特征

| 项目 | VitePress 值 |
| --- | --- |
| 正文颜色 | 浅色 `#3c3c43` / 深色 `#dfdfd6` |
| 页面背景 | 浅色 `#ffffff` / 深色 `#1b1b1f` |
| 品牌色 | indigo `#3451b2`（深色 `#a8b1ff`） |
| 链接 | 500 字重 + 下划线 + `text-underline-offset: 2px`，hover 变 `--vp-c-brand-2` |
| h1 / h2 / h3 / h4 | 32px·24px·20px·18px，字重 600，`letter-spacing: -0.02em / -0.01em` |
| h2 | 上方 1px 分隔线 + `padding-top: 1.5rem` + `margin-top: 3rem` |
| 段落 | `margin: 16px 0`，`line-height: 1.75`（28px） |
| 行内代码 | `#3451b2`、`rgba(142,150,170,.14)` 背景、圆角 4px、`padding: 3px 6px` |
| 代码块 | 背景 `--vp-c-bg-alt`、圆角 8px、`padding: 20px 0`、代码左右各 24px、`line-height: 1.7` |
| 代码高亮 | 逐 token 移植 shiki 的 `github-light` / `github-dark`（关键词红、实体紫、字符串深蓝、注释灰、标签绿） |
| 引用块 | `border-left: 2px solid var(--vp-c-divider)`、`padding-left: 1rem`、文字 `--vp-c-text-2` |
| 表格 | 表头 `#f6f6f7` 背景 + `--vp-c-text-2` 文字、14px、单元格 `padding: 8px 16px`、斑马纹 `--vp-c-bg-soft` |
| 分隔线 | 1px `--vp-c-divider` 实线（不是 GitHub 那种粗灰条） |
| 侧边栏 | `--vp-c-bg-alt` 背景，选中项用 `--vp-c-brand-soft` / `--vp-c-brand-1` |
| Mermaid | `--mermaid-theme` 跟随浅色/深色 |
| 深色模式 | 完整的一套深色 token，含 `--vp-c-bg: #1b1b1f`、代码块 `#161618`、边框 `#2e2e32` |

## 有意的偏离

为了让主题在「编辑器」而不是「文档站」里好用，下面几处没有 1:1 照搬 VitePress（其余属性经过逐条 computed-style 对比，完全一致）：

| 项目 | VitePress | 本主题 | 原因 |
| --- | --- | --- | --- |
| `h1` 下边距 | `0` | `1rem` | 文档站里 h1 只在页首出现；编辑器里 h1 可能出现在正文中间 |
| `h5` / `h6` 上边距 | `0` | `1.5rem` | 同上，避免与上一段贴死 |
| 表格 `display` | `block` | `table` | Typora 的表格拖拽/编辑依赖正常的 table 布局 |
| `<mark>` | 浏览器默认黄底黑字 | `--vp-c-warning-soft` 淡黄底 | 默认纯黄在深色模式下刺眼 |
| 行内/表内 `line-height` | 固定 px | 无单位 `rem` 派生 | 否则 Typora 的「字体大小」偏好会失效 |
| 字体栈 | `Inter, ui-sans-serif, system-ui, sans-serif` | `Ioskeley Mono` + `Sarasa Mono J`（CJK 回退） | 等宽字体阅读，见下 |
| 正文列宽 | 688px | 980px（normal），另有 fullwidth 变体 | Typora 是整窗编辑器，没有文档站侧边栏，688px 会白白浪费空间 |

## 内联字体

主题把两个开源字体直接嵌进 CSS（`@font-face` + `base64` data URI）。Typora 是 Electron/Chromium，
data URI 对它就等于一个普通字体文件，所以这样完全可行，代价只是 CSS 变大——换来的是装主题就等于装字体。

| | 字体 | 来源 | 内嵌内容 | 体积 |
| --- | --- | --- | --- | --- |
| 拉丁 | **Ioskeley Mono** | 官方 `IoskeleyMono-Web` WOFF2 | Regular / Bold / Italic / Bold-Italic | 408 KB |
| CJK | **Sarasa Mono J** | 官方发行版 TTF，构建时子集化 | Regular / Bold | 3.4 MB |

体积是按 base64 解码后的 WOFF2 算的；写进 CSS 后还要 ×4/3。

### CJK 子集覆盖了什么

Sarasa Gothic 一个 face 就有 26 MB（CJK 字形本身就是这个量级），四个 face 全量内联约 37 MB WOFF2 / 50 MB base64，
所以只内嵌常用部分（构建时选出的 **10 075 个码位**）：

- **GB2312 全集**：6763 个简体汉字，以及它自带的假名、希腊字母、西里尔字母、制表符
- CJK 标点与符号、全角/半角形式、平假名、片假名、CJK 兼容形式
- 常用代码符号：箭头、数学运算符、制表符、几何图形、货币、带圈数字等

**没有**覆盖：繁体专有字（如 `體`）、日文生僻字（如 `働`）、韩文（`한글`）、emoji、CJK 扩展区。
这些字符会落到字体栈里的下一个字体（`ui-monospace` → 系统 CJK 字体），因此不会出现豆腐块，
只是字形会跟 Sarasa 不一致。按需改 `tools/build-fonts.py` 里的字集即可。

> 斜体 CJK 没有单独内嵌：Chromium 会用 Regular 合成 oblique，实际观感差别很小，能省下 3.4 MB。

### 重新生成

内联块由脚本生成，头部有 `BEGIN INLINED FONTS` 标记：

```sh
uv run tools/build-fonts.py            # 重新生成 typora-vitepress.css
uv run tools/build-fonts.py --check    # CI 用：内容与脚本不一致就退出非 0
```

脚本会下载官方字体到 `tools/.cache/`（已 gitignore）并做子集化，输出是逐字节可复现的。
想换覆盖范围就改脚本里的 `CJK_EXTRA_RANGES`，想换成 SC 字形就把 `SarasaMonoJ-*` 换成 `SarasaGothicSC-*`
（改 `SARASA_URL` 与 `SARASA_FACES`）。

### 不想用内联字体？

- 想换成自己装的字体：把别的 family 放到 `--vp-font-family-*` 最前面即可，内联字体只是「兜底」，不会抢先。
- 想彻底去掉这 5 MB：删掉 CSS 里 `BEGIN INLINED FONTS` … `END INLINED FONTS` 之间的整块，
  然后自行安装这两个字体（[Ioskeley Mono](https://github.com/ahatem/IoskeleyMono)、[Sarasa Gothic](https://github.com/be5invis/Sarasa-Gothic)）。

## 自定义

> 下面所有改动建议写进主题文件夹里的 `typora-vitepress.user.css`，而不是直接改主题文件。
> Typora 的加载顺序是「主题 CSS → `base.user.css` → `{当前主题}.user.css`」，
> 文件名大小写敏感、前缀必须和主题文件名一致（`typora-vitepress`），这样主题更新时你的改动不会丢。

### 字体

正文与代码都使用：

```css
--vp-font-family-base: 'Ioskeley Mono', 'Sarasa Mono J', ui-monospace, … ;
--vp-font-family-mono: 'Ioskeley Mono', 'Sarasa Mono J', ui-monospace, … ;
```

- `Ioskeley Mono` 负责拉丁字符，字符宽 **0.6em**（16px 下 = 9.6px）
- `Sarasa Mono J` 负责 CJK，CJK 字符宽 **1em**（16px 下 = 16px），自身拉丁宽 0.5em

> ⚠️ 两个字体的字宽比是 **5:3 而不是 2:1**，所以中文不会正好落在「两个拉丁字符」的等宽网格上。想完全对齐有两种做法：
>
> 1. 把 `'Sarasa Mono J'` 放到拉丁字体之前（牺牲 Ioskeley Mono 的拉丁字形，但网格完美 2:1）
> 2. 保持现状，用 `font-size: 1.2em` 放大 CJK：`16px × 1.2 = 19.2px = 2 × 9.6px`，网格对齐但中文视觉上会大一号
>
> 只关心 CJK 用 SC 字形（简体字形而非日文字形）时，需要重新生成内联字体把 `Sarasa Mono J` 换成 `Sarasa Mono SC`，
> 详见上面「内联字体 → 重新生成」。只改 CSS 里的 family 名是没用的：内嵌的就是 J 的字形。

### 颜色

所有颜色、字号都集中在文件顶部的 `:root` 里，变量名与 VitePress 一致，例如把品牌色换成绿色：

```css
:root {
  --vp-c-brand-1: var(--vp-c-green-1);
  --vp-c-brand-2: var(--vp-c-green-2);
  --vp-c-brand-3: var(--vp-c-green-3);
  --vp-c-brand-soft: var(--vp-c-green-soft);
}
```

### 列宽

主题提供两份文件，靠 Typora 的 **主题** 菜单切换：

| 文件 | `--write-max-width` | 效果 |
| --- | --- | --- |
| `typora-vitepress.css` | `980px` | normal，默认。比 VitePress 自己的 688px 宽，因为 Typora 没有侧边栏 |
| `typora-vitepress-fullwidth.css` | `none` | fullwidth，铺满窗口，只留 32px 内边距 |

两份文件只差这一行声明，所以第二份是**生成**的，不是复制粘贴的：

```sh
uv run tools/build-fullwidth.py            # 重新生成 typora-vitepress-fullwidth.css
uv run tools/build-fullwidth.py --check    # CI 用：内容与基准文件不一致就退出非 0
```

改列宽时只改 `typora-vitepress.css` 里 `--write-max-width` 的值（例如 `1200px`）然后重跑脚本，
不要去改生成出来的那份——它开头的 banner 里也写了这一句。

### 深浅色

想固定用浅色（不跟随系统），可以把 `typora-vitepress.css` 里所有
`@media (prefers-color-scheme: dark) { ... }` 块删掉；
或者干脆：浅色模式选本主题，深色模式槽位选 Typora 自带主题。

## 调试

- macOS：Typora 偏好设置 → 通用 → 打开调试模式，重启后右键正文 → 检查元素
- 或 Safari → 开发 → 你的设备 → Typora

## 目录结构

```
typora-vitepress/
├── typora-vitepress.css             # 主题本体（normal，唯一手写的那份，含内联字体）
├── typora-vitepress-fullwidth.css   # fullwidth 变体（生成物，勿手改）
├── tools/
│   ├── build-fonts.py               # 生成内联字体块：下载 / 子集化 / base64
│   └── build-fullwidth.py           # 由主题本体生成 fullwidth 变体
├── licenses/
│   ├── OFL-IoskeleyMono.txt         # 内联字体的授权原文
│   └── OFL-SarasaGothic.txt
├── demo/
│   └── typora-vitepress-demo.md     # 覆盖全部样式的预览文档
└── README.md
```

## License

- 主题代码：MIT
- 内联字体：[Ioskeley Mono](https://github.com/ahatem/IoskeleyMono) 与 [Sarasa Gothic](https://github.com/be5invis/Sarasa-Gothic)，
  均为 SIL Open Font License 1.1，授权原文见 `licenses/`。Ioskeley Mono 未声明 Reserved Font Name；
  Sarasa Gothic 的 Reserved Font Name 是它内嵌 Adobe 字体部分所用的 `Source`，与嵌入的 `Sarasa Mono J` 无关，
  所以子集化后可以沿用原名。
