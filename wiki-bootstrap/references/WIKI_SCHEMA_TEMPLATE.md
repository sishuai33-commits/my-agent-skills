# WIKI_SCHEMA.md 模板

> 生成到目标 vault 的 `.claude/WIKI_SCHEMA.md`。
> 根据笔记工具类型调整 wikilink 语法：Obsidian/Logseq 用 `[[link]]`，纯文件夹/Notion 用 `[text](path.md)`。

---

## 完整模板

````markdown
# Wiki Schema 规则

> 专为 {笔记工具名} 设计的 Wiki 维护规则
> 遵循 Karpathy LLM Wiki 三层架构

---

## 架构说明

```
三层架构：
├── Raw Layer（原始层） - 原位置不动，只读
├── Wiki Layer（知识层） - wiki/ 目录，LLM 维护
└── Schema Layer（规则层） - 本文件
```

---

## 目录结构

```
wiki/
├── index.md           # 人机共读索引 + 关键词映射
├── .ai-vocab.md       # AI 知识地图（自动生成，含别名和时效）
├── log.md             # 操作日志
├── .dream-log.md      # Dream 维护日志
├── .dream-config.md   # Dream 配置（衰减参数、触发条件）
├── .dream-lock        # Dream 互斥锁
├── .dream-cursor.json # 提取游标（防重复）
├── .last_dream        # 上次 Dream 时间戳
├── .dream-count       # Dream 执行计数
│
├── entities/          # 跨项目共享的实体
├── concepts/          # 跨项目共享的概念
├── sources/           # 来源摘要
├── _archived/         # 日落归档（可恢复，90天后物理删除）
│
└── projects/          # 项目专属内容
    └── {项目名}/
        ├── synthesis.md   # 项目综述
        └── events/        # 项目事件
```

---

## 页面类型定义

### 实体页 (entities/)

跨项目共享的组织、团队、平台、人物。

**模板**：
```markdown
---
type: entity
category: organization | team | platform | person
created: YYYY-MM-DD
updated: YYYY-MM-DD
validated: YYYY-MM-DD
staleness: fresh | stale | outdated
confidence: EXTRACTED | INFERRED | AMBIGUOUS
relevance_score: 1.0
access_count: 0
last_access_date: YYYY-MM-DD
---

# {实体名}

## 基本信息
- 类型：{类型}
- 角色：{角色}

## 参与项目
- [[../projects/xxx/synthesis|项目名]]

## 参与事件
- [[../projects/xxx/events/yyy|事件名]]

## 来源追溯
> 置信度：{confidence}
> 原始资料：{来源}
```

### 概念页 (concepts/)

跨项目共享的概念、方法论、技术体系。

**模板**：
```markdown
---
type: concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
validated: YYYY-MM-DD
staleness: fresh | stale | outdated
confidence: EXTRACTED | INFERRED | AMBIGUOUS
relevance_score: 1.0
access_count: 0
last_access_date: YYYY-MM-DD
---

# {概念名}

## 定义
{一句话定义}

## 关键要点
- 要点1
- 要点2

## 相关实体
- [[../entities/xxx|实体名]]

## 来源追溯
> 置信度：{confidence}
> 原始资料：{来源}
```

### 项目综述页 (projects/{项目名}/synthesis.md)

项目整体概况。

**模板**：
```markdown
---
type: synthesis
project: {项目名}
created: YYYY-MM-DD
updated: YYYY-MM-DD
validated: YYYY-MM-DD
staleness: fresh | stale | outdated
confidence: EXTRACTED | INFERRED | AMBIGUOUS
relevance_score: 1.0
access_count: 0
last_access_date: YYYY-MM-DD
---

# {项目名}综述

## 项目定位
{一句话定位}

## 当前阶段
- 阶段：{阶段}
- 状态：{状态}

## 关键实体
| 实体 | 角色 |
|------|------|
| [[../../entities/xxx|实体名]] | {角色} |

## 关键事件
- [[events/xxx|事件名]]

## 来源追溯
> 编译来源：{来源列表}
```

### 事件页 (projects/{项目名}/events/)

项目相关的事件、会议、决策、里程碑。

**模板**：
```markdown
---
type: event
date: YYYY-MM-DD
status: planned | ongoing | completed
created: YYYY-MM-DD
updated: YYYY-MM-DD
validated: YYYY-MM-DD
staleness: fresh | stale | outdated
confidence: EXTRACTED | INFERRED | AMBIGUOUS
relevance_score: 1.0
access_count: 0
last_access_date: YYYY-MM-DD
---

# {事件名}

## 基本信息
- 时间：{日期}
- 类型：会议 | 决策 | 里程碑 | 对接

## 参与者
- [[../../../entities/xxx|实体名]]

## 待办事项
- [ ] 待办1

## 来源追溯
> 原始资料：{来源}
```

---

## 提取规则

### 触发条件

| 来源内容 | 创建页面类型 | 位置 |
|---------|------------|------|
| 新组织/团队/平台 | entity | entities/ |
| 新概念/术语/方法 | concept | concepts/ |
| 项目整体介绍 | synthesis | projects/{项目名}/ |
| 会议纪要/决策 | event | projects/{项目名}/events/ |
| 重要源文档 | source | sources/ |

### 置信度标注

**核心原则**：宁可标注 INFERRED，不要滥用 EXTRACTED。

| 等级 | 含义 | 触发条件（必须同时满足） |
|------|------|-------------------------|
| EXTRACTED | 直接来自原始资料 | ① 文档原文逐字/逐句提及 ② 无需任何补充、推断或解释 |
| INFERRED | 合理推论 | ① 文档提及相关内容 ② AI 补充了专业定义、上下文推断、跨文档关联 |
| AMBIGUOUS | 不确定 | ① 文档冲突/信息不足 ② 存在多种可能解释 ③ 包含"待确认"/"待定"等表述 |

**判断流程**：
```
内容是否在文档原文中出现？
├─ 是 → 是否需要补充专业定义或上下文？
│       ├─ 否 → EXTRACTED
│       └─ 是 → INFERRED（补充部分）
└─ 否 → 是否能根据上下文合理推断？
        ├─ 是 → INFERRED（记录推论依据）
        └─ 否 → AMBIGUOUS（标记待确认）
```

**字段级标注**（当页面包含混合置信度时使用）：

```markdown
## 基本信息
- **类型**：科技公司  <!-- EXTRACTED -->
- **角色**：平台运营方  <!-- EXTRACTED -->
- **核心能力**：数据处理、AI服务  <!-- INFERRED：根据"运营平台"推断 -->

## 待确认问题
- [ ] 具体技术栈  <!-- AMBIGUOUS：文档未提及 -->
```

---

## 操作流程

### Ingest（摄入）
读取新资料 → 提取实体/概念/事件 → 按模板创建页面（初始化 relevance_score=1.0） → 建立 [[链接]] → 更新 index.md 索引和关键词映射 → 重新生成 .ai-vocab.md → 追加 log.md

### Query（查询）
通过 obsidian MCP search_notes 搜索 wiki → 按需加载 1-3 页 → 融入回答。**每次查询触发记忆再巩固**：更新 access_count、last_access_date，距上次 validated >7 天则刷新。详细查询规则由 MEMORY.md 中的 wiki 指引驱动。

### Lint（检查）
孤儿页面、断链、矛盾信息、过时信息、relevance 异常、日落候选积压、.dream-lock 僵死

### Dream（梦境维护）
后台自动维护（子代理），四阶段：Orient → Gather Signal → Consolidate → Prune。三闸门触发（≥24h + ≥3 会话 + 无锁）。详细配置见 `wiki/.dream-config.md`

### Forget（智能遗忘）
基于多因素衰减模型，低 relevance 页面日落归档。四级阈值：>0.7🟢 / 0.3-0.7🟡 / 0.1-0.3🔴 / <0.1⚫sunset（7天缓冲 → _archived/ → 90天 → 物理删除）

---

## 时效与冲突规则

### 时效双标准

| 等级 | validated 距今 | relevance_score | 行为 |
|------|---------------|-----------------|------|
| 🟢 fresh | ≤ 30 天 | > 0.7 | 直接信任 |
| 🟡 stale | 31-60 天 | 0.3-0.7 | 提醒验证 |
| 🔴 outdated | > 60 天 | 0.1-0.3 | 必须先验证 |
| ⚫ sunset | — | < 0.1 | 日落候选 |

两标准不一致时以 relevance_score 为准。

### 知识冲突优先级
当前文件状态(最高) > Wiki validated 内容 > Wiki 未 validated 内容(最低)。冲突以文件为准。

### 关键词映射
格式：`{名称}/{别名} → {类型}/{文件名}`。新增自动追加，日落移除。

---

## .ai-vocab.md（AI 知识地图）

每次 ingest 后自动重新生成，包含：实体表（含口语化别名和时效标记）、概念表、项目表、近期事件(10条)、场景表。AI 在对话中首次遇到 wiki 话题时加载（~2KB），通过别名列做语义匹配。

---

## 注意事项

1. **原始资料不动**：Raw Layer 保持只读，不修改原位置文件
2. **增量更新**：每次只处理新增或变更的资料
3. **来源追溯**：每个页面必须有来源追溯部分
4. **置信度标注**：区分"找到的"和"猜的"
5. **所有页面必须包含 relevance_score / access_count / last_access_date**：为 Dream 衰减模型提供基线
````
