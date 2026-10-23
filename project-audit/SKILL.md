# project-audit — 独立批判性项目审计

独立视角的多维度项目审计体系。与日常代码审查不同：**使用不同模型获得真正的独立视角**，对抗性验证"建造者漏了什么"，重点查文档宣称与代码/数据实际之间的 gap。

## 触发

```
"审查XX项目" "评估XX" "XX项目有什么问题" "独立视角看XX"
"对XX做深度审计" "审计XX" "深挖XX项目"
```

## 核心原则

1. **异模型优先**：本审计建议使用与项目日常开发不同的模型执行（如项目日常用 DS → 审计用 GLM 5.2），以获得真正的独立视角。同模型审计 = 盲区重叠（proxy substitution 温床），异模型审计 = 强独立。
2. **消费方证据 > 代理指标**：不满足于"文件存在""exit 0""注册正确"，追到"真消费方执行证据"。
3. **宣称 vs 实际**：项目文档说 ✅ 的地方，去代码/数据里找反面证据。

## 三层审查体系

```
Tier 1: 自动化测试     Tier 2: 轻量对抗        Tier 3: 深度审计
  项目自己的 test       2-agent 双视角           3-round 深挖法
  每次改动跑            阶段结束时跑              里程碑/发版前跑
  <1min                  ~5min                    ~15min
  测"代码没坏"           测"没虚标✅"             测"方向没偏"
```

Tier 1 由项目自备（如 `bash test/run.sh`）。Tier 2/3 由本 skill 提供。

## 六维评估框架

| 维度 | 核心问题 |
|------|---------|
| 架构 | 概念地基自洽吗？架构图 vs 实现 gap 多大？ |
| 机制 | 核心闭环真在转还是代理指标虚标？ |
| 代码质量 | 死代码/重复/隐藏耦合/硬编码？机制vs资产分离？ |
| 测试 | 代理指标 vs 真行为断言比例？覆盖盲区？ |
| 数据完整性 | 文档宣称数据 vs 实际数据是否一致？ |
| 运营 | 复杂度趋势？外部验证？可持续性？ |

---

## Tier 2：轻量对抗审查

**触发**：每个开发阶段/Phase 结束时。指挥官说"审查一下XX项目"默认执行 Tier 2。

**流程**：

1. **DP-0 前置门禁**（`bash scripts/dp0-gate.sh <项目路径>`）：
   - □ 项目 test 全绿？（不绿 → 拒绝审计，先修测试）
   - □ 项目状态文件最近更新过？（STATE.md / README.md）
   - □ 上次审计 P0 是否全 closed？（未全关 → 警告，不强制拒绝）
   - 任一硬条件不满足 → 中止，输出"请先满足前置条件"

2. **Scope Fence**：根据项目 CLAUDE.md/STATE.md 自动声明审计范围（可改/不可改边界）

3. **派 2 agent 并行**：
   - **agent-1（代码审查）**：加载 `prompts/code-quality.md`，审代码正确性/过度设计/死代码/隐藏耦合
   - **agent-2（诚实性标注）**：加载 `prompts/honesty-check.md`，查 ✅ 标记是否有消费方证据支撑

4. **合并**：去重 → 按 P0/P1/P2 分类 → 每个发现带一行验证命令

5. **架构维度交叉标记**：若 agent-1（代码审查）在审查中发现以下模式，在合并报告中交叉标注为**同时也是架构问题**：
   - "Shell 和 Python 版本功能重叠" → 标记为架构冗余（技术栈未收敛），Tier 3 架构审查会深度追查
   - "已注册但生产环境 0 触发的 hook" → 标记为僵尸架构（生命周期问题），Tier 3 架构审查会深度追查
   - 见 `prompts/code-quality.md` §3（重复）和 §2（死代码）中"架构维度"标注

6. **快速路径升级**：P0 ≥ 3 或上次 Tier 3 > 14 天 → 自动建议升 Tier 3

**输出**：`<项目路径>/audit-reports/tier2-<date>.md`

---

## Tier 3：深度独立审计

**触发**：发版前 / 阶段切换 / 对外推广 / 指挥官说"深度审计"。Tier 2 发现 ≥3 P0 自动建议升级。

**三轮深挖法**：

### Round 1：文档层（1 agent）

读项目文档（CLAUDE.md / STATE.md / README / 架构设计文档）→ 形成**风险假设列表**。每个假设格式：`[维度] 假设描述 + 预测方向`。

### Round 2：代码层 + 数据层 + 架构层（4 agent 并行）

- **agent-1（代码审查）**：验证 Round 1 的代码相关假设 + 发现新问题
- **agent-2（测试质量）**：代理指标 vs 真行为断言比例 / 覆盖盲区 / mock 保真度
- **agent-3（数据取证）**：加载 `prompts/data-forensics.md` + 项目特定的数据检查清单。比对文档宣称 vs 实际数据
- **agent-4（架构审查）**：加载 `prompts/architecture-review.md`。检查六维框架中"架构"维度的每项问题：概念地基自洽性、CC 插件最佳实践符合性、内核与胶水分离、模块间数据流契约、架构冗余、复杂度预算、反馈闭环完整性。**参考外部标准优先**（CC 官方插件文档），不以项目自己的范式文档为标准

### Round 3：综合研判

合并 Round 2 发现 → 对照 Round 1 假设 → 输出：
- **假设验证率**：多少 Round 1 假设被坐实 / 推翻 / 仍不确定？
- **新发现**：Round 1 没预料到的问题
- **结论 + 数据 + 建议**：三块格式

**输出**：`<项目路径>/audit-reports/tier3-<date>.md`，含假设验证率。

---

## ke-audit 持久标记

审计发现的 P0/P1 可以持久化到被审代码中，下次审计自动检查：

```python
# ke-audit(P1,2026-07-05): 描述问题
#   验证: <一行命令，exit 0 = 已修复>
```

**管理命令**：
- `bash scripts/audit-marker.sh mark <file> <severity> <desc> <verify-cmd>` — 写入标记
- `bash scripts/audit-marker.sh check <project-path>` — 扫描所有标记，跑验证命令，输出 closed/recurred 状态
- `bash scripts/audit-marker.sh close <file> <marker-id>` — 验证通过后标 closed

---

## 严重度标准

| 级别 | 判据 | 示例 |
|------|------|------|
| P0 | 阻断性：机制在跑错误代码 / 数据完整性缺陷 / 安全关键代码零测试 | 调已归档停用的旧脚本 / pending 半数空裁决 |
| P1 | 高风险：跨组件隐藏耦合 / 代理指标代替真行为 / 大量代码零测试 | 动态 import 调内部函数 / 声明✅但无消费方证据 |
| P2 | 质量：断言强度/命名/注释/平台兼容性 | 跨平台 md5/md5sum 兼容 / 临时文件无 trap 清理 |

---

## 适用项目类型

任何有 CLAUDE.md + 状态文件的 CC 项目均可审计：
- **ke/tongle**：有 ke/dev/audit/ 专用扩展（Tier 3 数据取证 + ke 数据文件检查清单）
- **invest**：检查投资数据/持仓/DB 一致性
- **zhitong**：检查场景文档 vs 实际代码
- **量子项目**：检查业务资料 vs Wiki 结构
- **新项目**：帮助建立测试 + 审查基础设施

---

## 安装与依赖

- 本 skill 本身无外部依赖
- Tier 2/3 的 agent 调用依赖 CC 的 agent 基础设施（code-reviewer / general-purpose）
- 异模型审计依赖 CC 支持多模型切换
- `audit-marker.sh` 依赖 `bash` + `grep`
- `dp0-gate.sh` 依赖项目自备的测试入口（默认 `bash test/run.sh` 或 `bash dev/test/run.sh`）

---

## 关联

- ke 审计扩展：`~/Documents/My_Code_Projects/knowledge-engine/dev/audit/`（Tier 3 专用 + ke 数据取证提示）
- superpowers `verification-before-completion`（吸收：DP-0 门禁模式）
- superpowers `code-review`（吸收：prompt 结构）
- ponytail（吸收：`ponytail-debt` → `ke-audit` 标记格式）
- spec-superflow（吸收：Scope Fence + DP-0 硬门禁 + 快速路径升级）

---

## 版本记录

| 版本 | 日期 | 来源 | 变更说明 |
|------|------|------|----------|
| v1.1.0 | 2026-07-06 | 自建 | 新增架构审查 agent-4（Tier 3）+ 架构维度交叉标记机制（Tier 2 code-quality 识别 Shell/Python 重叠和僵尸 hook 时标记为架构问题）+ 新 prompt `architecture-review.md` |
| v1.0.0 | 2026-07-05 | 自建 | 初始版本：三层审查体系 + 六维框架 + ke-audit 标记 + 3 prompt 模板 + 3 脚本 |
