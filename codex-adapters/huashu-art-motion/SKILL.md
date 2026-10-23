---
name: huashu-art-motion
description: 制作或拆解艺术风格动画、口播解说动画、名画长卷和参数化视频片段；复用 Canvas 渲染引擎、风格配方与审片工具。普通静态绘图和仅音频任务不启动整片流程。
metadata:
  source_path: /Users/sishuai/Documents/My_Skills_Library/社区第三方/huashu-art-motion
  adapted_for: Codex
  source_version: 'git@57d6760'
  adapted_on: '2026-10-10'
---

# 艺术与解说动画

将一帧的构图、连续叙事与真实运动落实为可播放视频。沿用已确定的视觉方向；未定且影响成片时才做小样供选择，不强制三方向。

资源来自 CC/Pi 在用的 huashu-art-motion（MIT）。references、scripts、assets、schemas、defaults 指向共享原件，只读使用；新工程复制 `scripts/engine/` 后修改，不改原件。参考中的强制三选一、自动经验回流、固定人物服装推断不沿用；图片生成/编辑使用当前宿主 imagegen 和本次用户许可。

## 选择路径

| 任务 | 按需读取 |
|---|---|
| 拆解已有动画 | `references/01-拆解.md`、`references/02-机制.md` |
| 艺术风格动画 | `references/03-一帧先行四条路线.md`、`references/04-纯代码绘制.md`、`references/风格配方/INDEX.md`，再选一张配方 |
| 口播/科技/财经解说片段 | `references/09-视频动画语法.md` 与对应 `references/动画语法/` 卡；按 spec 契约渲染 |
| 长卷穿越多个画风 | `references/11-长卷穿越片.md`、`scripts/engine/demos/long_scroll/` |
| 完整口播片 | `references/12-口播整片与经验回流.md`；如涉及语音，另读 `references/capabilities.md` |
| 人物角色帧 | `references/10-角色.md`、`references/images.md`；先用已有素材或当前图像工具 |

## 工程使用

先检查 Python 的 playwright、Pillow、numpy，ffmpeg/ffprobe 及已装 Chromium。已具备时直接使用；缺依赖准确报告，不把安装或云服务配置默认为本次授权。无声片跳过语音配置；已有录音直接沿用，语音复刻单独按授权处理。

令 E 为复制后的工程绝对路径，S 为本技能绝对路径（shell 路径加引号）：

```sh
python3 "$E/render.py" --spec "$E/clip.json" --out "输出/片段.mp4"
python3 "$E/render.py" --solo 12_bauhaus --stills 0.5,1.5 --out "输出/关键帧"
# 参数化片段：审查同一份 spec
python3 "$S/scripts/qa.py" --project "$E" --spec "$E/clip.json" --out "输出/qa-clip"
# 整片/段落表：审查该工程的 eras；单风格可加 --ids 12_bauhaus
python3 "$S/scripts/qa.py" --project "$E" --out "输出/qa-film"
```

spec 字段、cue.kind 与该语法实际支持表对齐，未知 cue 可能无报错但不画；先出关键帧确认。统一随机种子，使同一时刻可重复渲染；每镜有主动作和适合风格的持续运动。财经数字和来源须准确，不能用动画改变数据含义。

## 验收

用 qa.py 核对确定性、运动、静止帧和文字框景，再实际看关键帧与成片；用 ffprobe 核对时长、画幅、帧率和音轨。浅底无字幕片按适用条件运行 scripts/subzone_gate.py。

对正式成片安排未参与制作的独立审片 agent，限定只读成片与 brief，不授予外发或配置权限；工具不可用时说明独立审片缺口，完成可做的实际检查。简单依赖自检不强制成片评审流程。交付区分脚本通过、视觉检查和独立审片结果；新经验留任务记录，修改共享技能另按授权处理。
