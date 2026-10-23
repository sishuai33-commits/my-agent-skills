---
name: wiki-bootstrap
description: Zero-config Wiki knowledge base deployment. Deploy Karpathy's three-layer LLM Wiki architecture with automatic environment probing, interactive personalization, and tool-specific adaptation (Obsidian/Logseq/Notion/plain folders). Use whenever users mention deploying wiki, setting up knowledge management, wanting systematic project knowledge, or organizing knowledge — even if they don't know Wiki architecture exists. Trigger on "wiki-bootstrap", "部署wiki", "搭建知识库", "初始化wiki", "知识管理", "wiki部署".
---

# Wiki Bootstrap — Wiki 知识体系一键部署

> 零门槛部署 Karpathy LLM Wiki 三层架构知识库。对方不需要懂 Wiki、不需要懂 Obsidian、不需要手动配置任何东西。安装此 skill，CC 自动探查环境、交互询问、个性化落地。

---

## 触发条件

### Slash Command

```
/wiki-bootstrap
```

### 自然语言触发

- "部署 wiki"、"初始化 wiki"、"搭建知识库"
- "帮我建立知识管理体系"
- "我想用 wiki 管理项目知识"

### 首次启动特殊处理

如果检测到当前环境**无任何 wiki 痕迹**（无 `wiki/` 目录、无 `WIKI_SCHEMA.md`、无 wiki-management skill），在会话开始时主动提示：

> 我注意到你还没有部署 Wiki 知识体系。要现在初始化吗？不会超过 5 分钟。

---

## 一、流程概览

```
探查 → 询问 → 设计 → 生成 → 安装 → 验证
(自动)  (交互)  (展示)  (创建)  (部署)  (测试)
```

| 阶段 | 耗时 | 说明 |
|------|------|------|
| 探查 | <10s | 自动扫描环境 |
| 询问 | 2-5min | 6-8 个问题 |
| 设计 | <30s | 输出落地方案 |
| 生成 | <1min | 创建目录和文件 |
| 安装 | <30s | 部署 wiki-management skill |
| 验证 | <1min | Smoke test |

---

## 二、Phase 1: 探查（自动）

### 2.1 笔记工具检测

按优先级依次检测，第一个命中即为候选：

| 工具 | 检测方法 | 置信度 |
|------|---------|--------|
| **Obsidian** | 检查 `~/Documents/Obsidian Vault/` 是否存在；或递归向上查找 `.obsidian/` 配置目录 | HIGH |
| **Logseq** | 检查 `~/Documents/Logseq/`；或查找 `logseq/` 目录 + `.git/config` 含 logseq | HIGH |
| **Notion** | 检查 MCP 配置中是否有 `notion` 相关 server；检查 `~/.claude/` 中是否有 notion 相关配置 | MEDIUM |
| **纯文件夹** | 以上均未命中，或用户显式指定一个目录 | — |

如果检测到多个工具同时存在（如同时有 Obsidian 和 Logseq），记录所有候选，待询问阶段让用户确认。

### 2.2 CC 环境检测

```
- CC 版本：claude --version
- Skills 目录：~/.claude/skills/ （全局）；<项目>/.claude/skills/ （项目级）
- 当前项目类型：git repo / plain dir / Obsidian vault
- 已有 MCP 配置：检查 settings.json 中 mcpServers
- 权限模式：检查 settings.json 中 permissionMode
```

### 2.3 项目目录探测

扫描以下典型路径，收集候选项目目录：

```
- ~/Documents/My_Code_Projects/
- ~/Documents/
- ~/Projects/
- ~/Code/
- 当前工作目录
- 用户 git repo 的 root 路径集合
```

对每个目录，记录：
- 路径
- 文件数量（是否活跃）
- 最近修改时间
- 是否有 `.claude/` 子目录（已在用 CC）

### 2.4 探查报告

探查完成后，简明汇报：

```
环境探查结果：

笔记工具：Obsidian（~/Documents/Obsidian Vault/）
CC 版本：v1.x.x
Skills 目录：~/.claude/skills/（全局）
已有 MCP：obsidian, tavily
候选项目目录（3个）：
  - ~/Documents/My_Code_Projects/项目A/  [活跃，已有 .claude/]
  - ~/Documents/My_Code_Projects/项目B/  [活跃]
  - ~/Code/learning-notes/              [低频]
```

---

## 三、Phase 2: 询问（交互）

### 3.1 问题设计原则

- 每个问题提供**默认值**（基于探查结果推测），用户可直接回车接受
- 使用**选择题**而非开放题，降低认知负担
- 总共 6-8 个问题，按依赖关系排序

### 3.2 问题序列

#### Q0: 确认笔记工具

（如果只检测到一个工具，跳过此问题，直接采用）

> 检测到你同时在用 Obsidian 和 Logseq，Wiki 知识层放到哪个工具里？
> [1] Obsidian
> [2] Logseq
> [3] 纯文件目录（指定路径）

#### Q1: 知识管理定位

> 你主要想用 Wiki 来管理什么？
> [1] 工作项目知识（业务实体、会议纪要、技术方案）
> [2] 个人学习笔记（概念、方法论、读书摘要）
> [3] 综合型（工作 + 学习都要）

这会影响初始目录结构和关键词预设。

#### Q2: 项目/数据源目录

> 需要纳入 Wiki 管理范围的项目目录有哪些？（多选）
> [列举探查到的候选目录，用户可勾选或追加]

对每个确认的目录，询问优先级：

> 哪些是 P0（每周编译）？哪些是 P1（每两周）？哪些是 P2（每月或手动）？

#### Q3: 额外数据源

> Wiki 还需要从哪些来源摄入知识？
> [1] 对话记录（CC 的 jsonl 会话历史）—— 可从对话中提取概念和决策
> [2] 外部 API（如 IMA 知识库、Notion API）—— 需要提供凭证
> [3] 暂不需要额外数据源

#### Q4: 定时编译与后台维护

> 是否需要定时自动编译和后台维护？
> [1] 是，每周一上午编译 + Dream 后台自动维护（推荐）
> [2] 仅手动触发编译
> [3] 自定义频率（请输入 cron 表达式）

#### Q5: 已有笔记处理

> 你的笔记工具里已经有一些笔记了，要如何处理？
> [1] 扫描现有笔记，执行首次全量编译
> [2] 仅搭建框架，后续增量添加
> [3] 先搭建框架，我指定哪些目录/笔记需要纳入

#### Q6: CLI 集成偏好（如果工具支持 MCP）

> Wiki 知识层需要与你的笔记工具深度集成吗？
> [1] 是，配置 MCP（CC 可直接读写笔记）—— 如果还没配的话
> [2] 否，纯文件操作即可

### 3.3 询问输出

收集完所有答案后，汇总确认：

```
配置确认：

笔记工具：Obsidian（~/Documents/Obsidian Vault/）
Wiki 位置：~/Documents/Obsidian Vault/wiki/
定位：工作项目型
P0 项目（每周）：项目A/
P1 项目（每两周）：项目B/
额外数据源：CC 对话记录
定时编译：每周一 8:57
已有笔记：首次全量编译
MCP 集成：是（Obsidian MCP）
```

询问用户 "以上确认？[Y/n]"。

---

## 四、Phase 3: 设计（展示方案）

基于配置，输出落地方案。此阶段仅展示，不做任何文件操作。

### 4.1 方案模板

```
═══════════════════════════════════════
  Wiki 知识体系部署方案
═══════════════════════════════════════

📁 目录结构：

~/Documents/Obsidian Vault/
├── wiki/                          # ← Wiki 层
│   ├── index.md                   #     人机共读索引 + 关键词映射
│   ├── .ai-vocab.md               #     AI 知识地图（含别名/时效，自动生成）
│   ├── log.md                     #     操作日志
│   ├── .dream-log.md              #     Dream 维护日志
│   ├── .dream-config.md           #     Dream 配置（衰减参数、触发条件）
│   ├── entities/                  #     实体（组织/团队/人物/平台）
│   ├── concepts/                  #     概念（术语/方法论/技术）
│   ├── projects/                  #     项目（综述 + 事件）
│   │   ├── 项目A/
│   │   │   ├── synthesis.md
│   │   │   └── events/
│   │   └── 项目B/
│   │       ├── synthesis.md
│   │       └── events/
│   ├── sources/                   #     来源摘要
│   ├── _archived/                 #     日落归档（可恢复）
│   └── .claude/
│       └── DATA_SOURCES.md        #     数据源配置
│
├── .claude/
│   └── WIKI_SCHEMA.md             # ← 规则层
│
└── [已有的笔记...]

🔧 技能安装：

~/.claude/skills/wiki-management/SKILL.md  ← wiki 维护技能

📊 数据源配置：

| ID | 名称 | 类型 | 路径 | 优先级 | 频率 |
|----|------|------|------|--------|------|
| ds-1 | 项目A | filesystem | ~/.../项目A/ | P0 | 每周 |
| ds-2 | 项目B | filesystem | ~/.../项目B/ | P1 | 每两周 |
| ds-3 | CC对话 | filesystem | ~/.claude/projects/ | P1 | 每周 |

⚙️ 自动化：

- 定时编译：每周一 8:57（待配置 crontab）
- Dream 后台维护：24h + 3新会话自动触发（Orient→Signal→Consolidate→Prune）
- 智能遗忘：低 relevance 页面自动日落归档（7天缓冲 → _archived/ → 90天删除）
- MCP 集成：Obsidian MCP（已配置 / 待配置）

🔜 初始化后会执行：

- 首次全量编译（扫描所有数据源 + 已有笔记）
- 生成 .ai-vocab.md AI 知识地图
- 初始 Dream 基线扫描（注入 relevance_score 字段）
- 输出知识库健康报告
```

### 4.2 用户确认

展示方案后等待确认。用户可调整任何配置项。

---

## 五、Phase 4: 生成（创建文件）

用户确认后，依次创建所有文件。**每创建一个文件后简要报告进度**。

### 5.1 创建目录结构

```bash
mkdir -p wiki/{entities,concepts,projects,sources,.claude}
```

### 5.2 写入 WIKI_SCHEMA.md（规则层）

必须生成到目标 vault 的 `.claude/WIKI_SCHEMA.md`（如果是纯文件夹模式，则生成到目标目录的 `.claude/WIKI_SCHEMA.md`）。

**模板内容**：读取 [`references/WIKI_SCHEMA_TEMPLATE.md`](references/WIKI_SCHEMA_TEMPLATE.md)，按其完整模板生成，并根据工具类型调整：
- Obsidian 用户：保留 `[[wikilink]]` 语法
- 纯文件夹/Notion 用户：`[[wikilink]]` 改为 Markdown 标准链接 `[text](path.md)`
- Logseq 用户：保留 `[[wikilink]]` 语法

### 5.3 写入 DATA_SOURCES.md

生成到 `wiki/.claude/DATA_SOURCES.md`。

模板结构：
```markdown
# Wiki 数据源配置

> 定义 Wiki 知识库的素材来源和同步规则

---

## 数据源列表

| ID | 名称 | 类型 | 状态 | 优先级 |
|----|------|------|------|--------|
{根据 Q2/Q3 的回答动态生成}

---

## 数据源详情

{对每个数据源生成详情章节，包含路径、扫描规则、文件类型、增量检测方式}

---

## 增量检测流程

{根据 Q4 的定时编译配置生成}

---

## 版本记录

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0.0 | {今天日期} | Wiki Bootstrap 初始化配置 |
```

### 5.4 写入 index.md

生成的 index.md 做三件事：
1. 标注 `最后更新` 和 `知识库规模`（初始为 0）
2. 根据 Q1/Q2 的回答预设关键词映射（如已确认的项目名、工具名、已知概念）
3. 保留实体/概念/项目/来源的索引表框架，等待首次编译填充

**重要**：不编造任何知识内容。索引表保持空（`暂无`），关键词映射可预设已确认的项目名。

### 5.5 写入 log.md

```markdown
# Wiki 操作日志

## [YYYY-MM-DD] bootstrap | Wiki 体系初始化

**操作**：Wiki Bootstrap 部署
**配置摘要**：
- 笔记工具：{工具名}
- 数据源：{数量} 个
- 定时编译：{是/否}
- 首次编译：{待执行/已完成}
```

### 5.6 生成进度汇报

```
文件创建进度：
✅ wiki/                         — 目录结构
✅ WIKI_SCHEMA.md                — 规则层
✅ wiki/index.md                 — 总索引
✅ wiki/log.md                   — 操作日志
✅ wiki/.claude/DATA_SOURCES.md  — 数据源配置
⬜ wiki-management skill         — 待安装
⬜ 首次编译                      — 待执行
```

---

## 六、Phase 5: 安装（部署技能）

### 6.1 生成并安装 wiki-management skill

根据探测的工具类型，生成对应的 `SKILL.md`，安装到目标 skills 目录。

**全局安装**（推荐）：
```
~/.claude/skills/wiki-management/SKILL.md
```

**项目级安装**（如果当前在 project vault 内）：
```
<vault>/.claude/skills/wiki-management/SKILL.md
```

**生成规则**：`wiki-management` skill 的核心结构必须包含：

```
# Wiki 知识体系维护

## 一、触发条件（自动触发 + 用户指令）
## 二、架构说明（三层架构图 + 目录结构，含 _archived/ 和 .dream-* 文件）
## 三、核心操作
### 3.1 Ingest（知识摄入）— 初始化 relevance_score/access_count
### 3.2 Query（知识查询）— 三层检索 + 记忆再巩固副作用
### 3.3 Lint（健康检查）— 含 relevance/dream-lock/sunset 检查
### 3.4 Dream（梦境维护）— 四阶段后台自动维护（子代理）
### 3.5 Forget（智能遗忘）— 多因素衰减 → 日落归档
## 四、知识生命周期（诞生 → 演进 → 合并 → 日落 → 删除）
## 五、时效与置信度（双标准：staleness + relevance_score）
## 六、卡片盒方法与链接
## 七、定期审视（周 lint / 月审视 / 季深度）
## 八、数据源管理
```

**注意**：页面模板详情和衰减公式参数不在 SKILL.md 中重复，改为引用 WIKI_SCHEMA.md（格式定义）和 .dream-config.md（参数配置）。

### 6.2 工具特定适配

在生成 wiki-management skill 时，根据工具类型调整：

| 工具 | 调整项 |
|------|--------|
| Obsidian | Wikilink `[[ ]]` 语法、MCP 集成说明、Obsidian Graph View 关联 |
| Logseq | Logseq 命名约定（`page.md` vs `Page Name.md`）、块引用 `(( ))` |
| Notion | Notion MCP 调用方式、database 同步说明 |
| 纯文件夹 | Markdown 标准链接、无 MCP，纯文件操作 |

### 6.3 安装汇报

```
✅ wiki-management skill 已安装到 ~/.claude/skills/wiki-management/
   重启 CC 或新开会话即可使用以下命令：
   - "编译 wiki" / "ingest"
   - "wiki 状态"
   - "lint" / "健康检查"
```

---

## 七、Phase 6: 验证（测试）

### 7.1 Smoke Test

执行一个最小化的 ingest 验证：

1. 如果用户选了 Q5-[1]（编译已有笔记），执行首次编译
2. 如果选了 Q5-[2]（仅框架），跳过
3. 如果选了 Q5-[3]（指定范围），按指定范围编译

### 7.2 输出知识库地图

```
═══════════════════════════════════════
  🎉 Wiki 知识体系部署完成！
═══════════════════════════════════════

📊 知识库状态：
  - 实体：0（等待首次编译填充）
  - 概念：0
  - 项目：{已在 index 中预设的数量}
  - 事件：0
  - 所有页面已注入 relevance_score / access_count / last_access_date（初始基线）

🔗 关键路径：
  - 知识层：{wiki 目录绝对路径}
  - 规则层：{WIKI_SCHEMA.md 绝对路径}
  - Dream 配置：wiki/.dream-config.md
  - 维护技能：~/.claude/skills/wiki-management/

💡 接下来你可以：
  1. 说"编译 wiki" — 执行首次知识摄入
  2. 说"wiki 状态" — 查看知识库概览
  3. 在日常对话中自然提到项目/概念 — Wiki 自动按需加载（三层检索）
  4. Dream 后台维护自动触发（≥24h + ≥3会话），无需手动操作
  5. 说"整理 wiki" — 手动触发 Dream
```

### 7.3 首次编译（可选）

如果用户选择了 Q5-[1] 扫描已有笔记，在验证阶段执行首次编译。流程同 wiki-management 的 ingest：
- 扫描所有数据源
- 提取实体/概念/事件
- 生成初始 Wiki 页面
- 更新 index.md

---

## 八、参考文件

本 skill 的核心模板和适配参数已拆分到独立参考文件，在对应阶段按需读取：

| 阶段 | 读取文件 | 用途 |
|------|---------|------|
| Phase 4 (生成) | [`references/WIKI_SCHEMA_TEMPLATE.md`](references/WIKI_SCHEMA_TEMPLATE.md) | WIKI_SCHEMA.md 完整模板，含页面类型定义、置信度体系、时效标记 |
| Phase 2 (询问) | [`references/interview-prompts.md`](references/interview-prompts.md) | 边界场景追问话术（工具未检测到、项目缺失、冲突处理等） |
| Phase 1 (探查) / Phase 5 (安装) | [`references/tool-adapters.md`](references/tool-adapters.md) | Obsidian/Logseq/Notion/纯文件夹 的链接语法、MCP 配置、wiki-management 生成规则 |

**读取时机**：在进入对应阶段时加载相应参考文件，而非启动时全部预载。

---

## 十一、错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| 目标目录无写权限 | 提示用户检查权限，或更换目录 |
| 目标 `.claude/WIKI_SCHEMA.md` 已存在 | 询问：覆盖 / 合并 / 跳过 |
| 目标 `wiki/` 目录已有内容 | 询问：覆盖 / 保留并合并 / 更换位置 |
| `wiki-management` skill 已安装 | 比较版本，询问是否更新 |
| MCP 配置失败 | 降级为纯文件操作，标注"待配置" |
| 首次编译失败 | 输出错误详情，建议手动排查或缩小编译范围 |

---

## 十二、交互风格的额外要求

- **全中文交互**，技术术语保留英文
- **每阶段给进度条感**："探查完成 → 接下来问几个问题 → 方案出来了 → 开始创建文件..."
- **允许用户随时中断**，已创建的文件不丢失，下次可继续
- **不允许编造内容**：index.md 初始索引可为空，不可编造实体/概念
- **最小化打扰**：能默认的给默认，能跳过的跳过

---

## 版本记录

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.1.0 | 2026-05-06 | 拆分附录为独立参考文件（WIKI_SCHEMA_TEMPLATE / interview-prompts / tool-adapters），添加 YAML frontmatter，新增 evals 测试用例 |
| v1.0.0 | 2026-05-06 | 初始版本：六阶段部署流程、工具适配、WIKI_SCHEMA 模板、wiki-management 技能生成 |
