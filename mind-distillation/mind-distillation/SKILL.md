---
name: mind-distillation
description: 从博主内容中萃取方法论，让AI模拟专家思维
user_invocable_skills:
  - crawl: 爬取知识星球博主内容
  - extract: 从数据中萃取方法论
  - evaluate: 迭代验证（AI模拟vs博主真实）
  - iterate: 增量更新方法论
---

# 思维刻录 Skill

**核心价值**：从博主的知识资料中萃取方法论，让AI能够模拟该领域的专家思维。

## 核心方法：迭代螺旋

```
新问答/文章 ──► AI模拟回答 ──► 对比博主真实 ──► 分析差距 ──► 更新方法论
                                                              │
                                                              ▼
                                                         下轮验证
```

**每次迭代记录**：
- 风格相似度（0-10）
- 框架遵循度（0-10）
- 实用价值（0-10）
- 人味评分（0-10）

## 使用场景

- 想让AI模拟某个博主的回答风格和决策思路
- 将散落的问答/文章结构化为可复用的方法论
- 持续迭代优化方法论，追踪质量变化

## 快速开始

```bash
# 1. 爬取博主内容
/mind-distillation crawl --source zsxq --user zhongyuan

# 2. 萃取方法论
/mind-distillation extract --case zhongyuan

# 3. 迭代验证（核心）
/mind-distillation evaluate --case zhongyuan --questions 5

# 4. 增量迭代
/mind-distillation iterate --case zhongyuan --new-data ./new-qa.json
```

## 当前案例状态

**重远投资观（zhongyuan）**：
- 楼市方法论：v3.0（深层萃取 + 人味 + 市场轮动）
- 股市方法论：v1.0（复用楼市经验）
- 第一轮验证完成，主要差距：回答太详细、缺少具体点位、新变量敏感度低

## 目录结构

```
mind-distillation/cases/zhongyuan/
├── data/
│   ├── articles/           # 原始文章
│   ├── qa/                 # 原始问答
│   └── articles-full/      # 完整精华文章
├── methodology-real-estate-deep.md  # 楼市方法论 v3.0
├── methodology-stock-deep.md        # 股市方法论 v1.0
├── iteration-log.md        # 迭代验证日志
├── maintenance-plan.md     # 维护计划
└── crawl-report.md         # 爬取报告
```

## 质量目标

| 指标 | 当前 | 目标 | 说明 |
|------|------|------|------|
| 风格相似度 | 6-7/10 | 8/10 | AI回答像博主的程度 |
| 框架遵循 | 8/10 | 9/10 | AI正确应用方法论的程度 |
| 实用价值 | 7/10 | 8/10 | 回答的可操作性 |
| 人味评分 | 6/10 | 8/10 | 有温度、有共情的程度 |

## 维护机制

| 任务 | 频率 | 触发条件 |
|------|------|----------|
| AI模拟vs博主对比 | 每次 | 用户提问时 |
| 方法论版本升级 | 发现重要差距后 | 验证结果 |
| 研讨小结更新 | 每次有实质进展 | 迭代完成 |

## 详细命令

### /crawl - 爬取数据
从知识星球爬取博主的精华文章和问答。

### /extract - 萃取方法论
从原始数据中萃取出结构化的方法论（深层萃取：洞察→逻辑→制约→场景→人味）。

### /evaluate - 迭代验证
让AI用方法论模拟回答，对比博主真实回答，分析差距，更新方法论。

### /iterate - 增量迭代
根据新数据或验证结果迭代方法论，记录版本变化。