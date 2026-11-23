# 技能库_自建

本目录保存自建技能原件及未在役的历史资产，不等于当前宿主的可用技能清单。版本、用途和规则以各技能 `SKILL.md` 为准；发现状态须核当前宿主的配置、链接与实际加载，不再用一张静态版本表代替。

## 原件与发现入口

2026-11-16 对 `~/.claude/skills/`、`~/.agents/skills/` 的文件级核对：以下本目录原件有入口，两个入口指向同一 realpath 不算两套技能：

- `4a-collaborator/`：方案与架构协作。
- `a-stock-data/`：行情与投研数据代码示例。
- `ai-maintenance/`：有界AI环境审查与授权修复。
- `skills-management/`：来源、部署、回退及验收。
- `chen-laoshi-perspective/`、`fu-peng-perspective/`：有来源和适用边界的方法参考，不是真人或收益保证。
- `xiaohongshu/`：已有浏览器能力下的内容提取。

本次核对只证明链接和文件存在，不证明外部接口、各端原生运行或效果。

## 项目维护的共享原件

| 对象 | 唯一原件 |
|---|---|
| card-compiler | `~/Documents/My_Code_Projects/tongle/skills/card-compiler/`；本目录旧副本已归档 |
| invest | `~/Documents/My_Code_Projects/invest-assistant/` |
| nuwa / huashu-nuwa | `~/Documents/My_Skills_Library/社区第三方/nuwa-skill/`；发现入口为软链，属于第三方包及本地适配，不是发现目录直下独立原件 |

`codex-adapters/`保存宿主适配入口，不是上游正文副本；其在役状态按该宿主实际发现配置核对。`source_version`是派生基线，不能仅因上游版本变了就改字段冒充已重新适配。

## 未在上述两根发现的库内资产

`commander-perspective/`、`mind-distillation/`、`project-audit/`、`wiki-bootstrap/`、`n8n-docker-upgrade/`、`bjc-reimbursement/`仍保留原件。未挂载不等于无价值、也不证明所有其他宿主都停用；需要时先核现状与授权，不因关键词自动恢复。

- `mind-distillation/`有嵌套同名历史入口，未因本轮审查删除。
- `bjc-reimbursement/`保留小写`skill.md`，跨平台发现尚未核验。
- `project-audit`元数据、n8n升级/备份安全承诺等已列本轮待核，未启动这些资产或执行其命令。

## 使用与维护

已发现技能可按任务调用；安装、恢复、停用和升级按 `skills-management` 与当前授权执行。停止本轮使用不等于撤除发现入口，撤除入口也不等于删除原件。

修改解析后的唯一源，保留回退和共享影响；只修任务相关问题，不自动pull/push或恢复旧服务。实际变更记 `../.skills-changelog.md`。2026-11-16本轮证据与覆盖位于 `../.audit-20261116/`，这只是维护证据，不是第二份技能真源或常驻任务系统。
