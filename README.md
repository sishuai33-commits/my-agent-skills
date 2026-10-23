# 技能库_自建

自建 Skills 存放目录，由指挥官自行审查和维护。

> 登记口径（2026-08-16 补登 4->13）：逐目录核对 SKILL.md 的 name/description；多数无 version 字段标 `-`，有据可查的如实填。nuwa（女娲造人）实体不在本目录，位于 `~/.claude/skills/nuwa/` 直下，不在此表。

---

## 当前 Skills（13）

| Skill | 用途 | 版本 |
|-------|------|------|
| skills-management | Skills 全生命周期管理（安装评估/安全审查/版本管理/激活禁用） | v2.0 |
| card-compiler | 卡片盒×LLM Wiki 卡片编译与项目卡片化拆解（原子卡/hub/指针卡规范 + 五问九步流程）；**真源在 `~/Documents/My_Code_Projects/tongle/skills/card-compiler`，本目录旧副本已归档** | - |
| 4a-collaborator | 4A 架构方法论->AI 执行桥梁：项目场景梳理、真源属性图、架构图产出 | - |
| a-stock-data | A 股全栈数据工具包：行情/研报/信号/资金面/新闻/基础数据/公告七层 | - |
| chen-laoshi-perspective | 陈老师（重远投资观）思维操作系统：宏观/A股/楼市/微观验证 | v0.5.0 |
| fu-peng-perspective | 付鹏思维操作系统：全球流动性/FICC 跨资产/AI 产业周期 | - |
| commander-perspective | 指挥官方法论操作系统：五层认知框架，原则对照审查与质量验收 | - |
| mind-distillation | 从博主内容萃取方法论，让 AI 模拟专家思维（nuwa 前身） | v1.0 |
| xiaohongshu | 小红书内容抓取：搜索/笔记详情+评论/用户主页（依赖 browser-act） | - |
| project-audit | 独立批判性项目审计：异模型对抗视角查"建造者漏了什么" | - |
| wiki-bootstrap | Zero-config Wiki 知识库部署（Karpathy LLM Wiki 路线） | - |
| bjc-reimbursement | 佰钧成差旅报销助手：备案信息->报销材料包 | v1.0 |
| n8n-docker-upgrade | 一键升级 Docker 版 n8n | v1.0 |

---

## 目录结构

```
技能库_自建/
├── skills-management/
├── card-compiler/   （已归档：真源在项目仓 tongle）
├── 4a-collaborator/
├── a-stock-data/
├── chen-laoshi-perspective/
├── fu-peng-perspective/
├── commander-perspective/
├── mind-distillation/
├── xiaohongshu/
├── project-audit/
├── wiki-bootstrap/
├── bjc-reimbursement/
└── n8n-docker-upgrade/
```

---

## 使用方式

1. **激活**：对话中说"需要用 xxx skill"
2. **禁用**：说"用完了"或"删掉 xxx"

---

> 详细管理流程见 `/skills-management` 技能
