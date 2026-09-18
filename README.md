# Typora VitePress Theme

让 Typora 拥有 [VitePress](https://vitepress.dev) 默认文档站点的排版与配色。

主题直接复用了 VitePress 自己的 CSS 变量命名（`--vp-*`），因此任何熟悉 VitePress 定制方式的人，可以用完全相同的思路来改这个主题。

- 参考基准：`vitepress@1.6.4`（`src/client/theme-default/styles/`）
- 单一 CSS 文件：`typora-vitepress.css`
- 通过 `prefers-color-scheme` 自动跟随系统切换 **浅色 / 深色**，无需第二个主题文件
- 正文字号全部使用 `rem`，Typora 的「字体大小」偏好设置依然生效

## 安装

1. 打开 Typora → 偏好设置 → 外观 → **打开主题文件夹**
2. 把 `typora-vitepress.css` 复制进去
3. 重启 Typora，在 **主题** 菜单里选择 `Typora Vitepress`

> macOS 上主题文件夹通常是 `~/Library/Application Support/abnerworks.Typora/themes/`。

## 还原了哪些 VitePress 特征

| 项目 | VitePress 值 |
| --- | --- |
| 正文列宽 | 688px（`#write` = 688 + 2×32px gutter） |
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

## 自定义

### 字体

正文与代码都使用：

```css
--vp-font-family-base: 'Ioskeley Mono', 'Sarasa Mono J', ui-monospace, … ;
--vp-font-family-mono: 'Ioskeley Mono', 'Sarasa Mono J', ui-monospace, … ;
```

- `Ioskeley Mono` 负责拉丁字符，字符宽 **0.6em**（16px 下 = 9.6px）
- `Sarasa Mono J` 作为 CJK 回退，CJK 字符宽 **1em**（16px 下 = 16px），自身拉丁宽 0.5em

> ⚠️ 两个字体的字宽比是 **5:3 而不是 2:1**，所以中文不会正好落在「两个拉丁字符」的等宽网格上。想完全对齐有两种做法：
>
> 1. 把 `'Sarasa Mono J'` 放到拉丁字体之前（牺牲 Ioskeley Mono 的拉丁字形，但网格完美 2:1）
> 2. 保持现状，用 `font-size: 1.2em` 放大 CJK：`16px × 1.2 = 19.2px = 2 × 9.6px`，网格对齐但中文视觉上会大一号
>
> 只关心 CJK 用 SC 字形（简体字形而非日文字形）时，把 `'Sarasa Mono J'` 换成 `'Sarasa Mono SC'`。

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

改列宽：

```css
#write {
  max-width: 852px; /* 720px 正文 + 2×32px gutter */
}
```

想固定用浅色（不跟随系统），可以把 `typora-vitepress.css` 里所有
`@media (prefers-color-scheme: dark) { ... }` 块删掉；
或者干脆：浅色模式选本主题，深色模式槽位选 Typora 自带主题。

也可以不去改主题文件，按官方文档的方式在主题文件夹里新建
`typora-vitepress.user.css` 覆盖（这样主题更新时你的改动不会丢）。

## 调试

- macOS：Typora 偏好设置 → 通用 → 打开调试模式，重启后右键正文 → 检查元素
- 或 Safari → 开发 → 你的设备 → Typora

## 目录结构

```
typora-vitepress/
├── typora-vitepress.css          # 主题本体（唯一需要安装的文件）
├── demo/
│   └── typora-vitepress-demo.md  # 覆盖全部样式的预览文档
└── README.md
```

## License

MIT
