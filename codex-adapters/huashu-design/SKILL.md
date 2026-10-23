---
name: huashu-design
description: 用本地 HTML 制作高保真原型、演示页面、HTML 幻灯片和产品动效；复用花叔设计素材与导出工具。Figma、在线网站发布、会话内交互解释及
  PowerPoint 文件按当前宿主对应技能处理。
metadata:
  source_path: /Users/sishuai/Documents/My_Skills_Library/社区第三方/huashu-design
  adapted_for: Codex
  source_version: '2.1.0'
  adapted_on: '2026-10-10'
---

# HTML 视觉设计

以用户已有品牌、页面、截图和项目样式为起点。先确定观众、主要操作和交付媒介，再选字体、色板、版式与关键动效；使用项目局部 token。已有方向直接实现；仅在方向确实未定且会明显影响结果时提供可比较的小样，不强制三版或多轮审批。

本入口适配 CC/Pi 在用的 huashu-design，复用同一原件的 references、assets、scripts（MIT）。这些目录是共享只读资源：需要修改时复制到任务工程。正文与参考冲突时按本入口及当前宿主规则执行；参考中的固定三方向、默认推广水印、按模型降级、自动写技能库、自动版本检查不沿用。不要把演示用 API 密钥写进前端。

## 按产物取资源

- 本地 HTML 原型：`references/content-guidelines.md`、`references/typography.md`；React/Babel 项目再读 `references/react-setup.md`，手机外框按需用 `assets/ios_frame.jsx`。
- 风格未定：`references/design-styles.md` 和 `assets/showcases/INDEX.md`。
- HTML deck：`references/slide-decks.md`、`assets/deck_index.html`；用户要可编辑 PowerPoint 时由当前 presentations 技能主导，按需参考 `references/editable-pptx.md`。
- 产品 UI 动画：先读 `references/storyboard-basics.md`、`references/ui-demo-animation.md`、`references/animation-pitfalls.md`，镜头实现再读 `references/camera-language.md`、`references/gsap-recipes.md`。
- 导出视频：`references/video-export.md`；按工程所用时间轴选 `scripts/render-video.js` 或 `scripts/render-video-seek.js`。先检查现有运行时和依赖，不自动升级、装软件或接入云配音。
- 带口播：`references/voiceover-pipeline.md`；沿用用户给的音频。新语音服务、付费调用按本次授权处理。

## 制作与验收

先让关键画面成立，再扩到完整流程；实际文案和数据优先，示例数据明确标示。动效应承载解释、转场或操作反馈。复杂度随产物规模决定，不为小改动搭建新框架。

在真实浏览器检查关键尺寸、交互、长中文、溢出、空态和控制台错误。`references/verification.md` 仅取检查项；其中 CC 绝对路径、自动安装示例和 `page.video.record` 旧调用不适用。可运行当前技能绝对路径下的 `scripts/verify.py`（先看 --help），输出指定到任务目录；录屏遵循当前可用浏览器 API。动画检查开始、中间、结束和转场，视频检查时长、分辨率、画面与音轨。只有 HTML 或脚本检查通过不能称为成片验收。

交付用户要求的文件并打开预览。原型不自动变为线上发布，不因使用本技能修改共享素材或知识库。
