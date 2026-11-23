---
name: huashu-design
description: 用本地 HTML 制作高保真原型、App/微信小程序原型、App Store 宣传图、HTML 幻灯片和产品动效；复用花叔设计 3.5 模块手册与校验工具。Figma、在线网站发布、会话内交互解释及可编辑 PowerPoint 文件按当前宿主对应技能处理。
metadata:
  source_path: /Users/sishuai/Documents/My_Skills_Library/社区第三方/huashu-design
  adapted_for: Codex
  source_version: '3.5.0'
  adapted_on: '2026-11-23'
---

# HTML 视觉设计

以用户已有品牌、页面、截图和项目样式为起点。先用用户已给且适用于本次交付的材料；仅对影响交付的未知或时效事实补查，不把私有需求外发公开搜索。先确定观众、主要操作和交付媒介，再选字体、色板、版式与关键动效；使用项目局部 token。已有方向直接实现；仅在方向确实未定且会明显影响结果时提供可比较的真实初稿，不强制三版或多轮审批。

本入口适配 CC/Pi 在用的 huashu-design 3.5（MIT），复用同一原件的 `references/`、`assets/`、`scripts/`。这些目录是共享只读资源：需要修改时复制到任务工程。正文与参考冲突时按本入口及当前宿主规则执行；参考中的固定三方向、按模型品牌分档、默认推广水印、自动写共享技能库、自动版本检查不沿用。不要把演示用 API 密钥写进前端。

## 按产物取模块手册（v3.5 路由）

- 网页 / 落地页 / Dashboard / 桌面原型：`references/modules/web.md`，搭配 `references/content-guidelines.md`、`references/typography.md`；React/Babel 读 `references/react-setup.md`。
- 手机 App / iOS 原型：`references/app-prototype.md`、`references/app-paradigms.md`，外框按需用 `assets/ios_frame.jsx` 与 `assets/showboard.jsx`。
- 微信小程序原型与交付包：`references/modules/miniprogram.md`（外框 `assets/wechat_frame.jsx`，交付体检 `scripts/mp_handoff.py`）。
- App Store 宣传图：`references/modules/appstore.md`、`assets/appstore/template.html`。
- 风格探索与参照：`references/design-styles.md`、`references/directions.md`、`assets/style-specimens/`；环境受限时走 `references/steady-track.md`。
- HTML deck：`references/modules/deck.md`；用户明确要可编辑 PowerPoint 时优先由当前宿主 PPTX 技能主导，不强制 HTML-first。
- 信息图 / 小红书图文：`references/modules/infographic.md`、`references/modules/xiaohongshu.md`。
- 产品 UI 动画与视频导出：`references/modules/motion.md`；先核对现有运行时和依赖（`scripts/capabilities.py`），不自动升级、装软件或接入付费云配音。
- 设计评审：`references/critique-guide.md`。

## 制作与验收

先让关键画面成立，再扩到完整流程；实际文案和数据优先，示例数据明确标示。优先使用真实图片或授权素材，不用 emoji/灰色占位块冒充真图；复杂度随产物规模决定，不为小改动搭建新框架。

交付前在真实浏览器检查关键尺寸、交互、长中文、溢出、空态和控制台错误。可按需使用当前技能绝对路径下的只读/本地工具（先看 `--help`，输出指定到任务目录）：
- `scripts/polish.py shot`：逐屏截原图并做看图打磨（App/小程序展示板不加 `--mobile`）。
- `scripts/design_lint.py check`：排查红灯与模板装饰黄灯。
- `scripts/offline.py`：含 CDN React/Babel/字体时打包为断网可开单文件。
- `scripts/verify.py`：常规双视口渲染与控制台校验。

`references/verification.md` 仅取检查项；其中 CC 绝对路径、自动安装示例和旧 API 不适用。缺少看图能力或依赖时如实标明未验证，脚本跳过不算通过。交付用户要求的文件，不自动线上发布，不修改共享素材或知识库。
