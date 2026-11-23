# 上游与升级说明

<!-- skills-check: upstream=https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/SKILL.md version=3.10.4 sha256=09f7e8a3f826f747d293a1e86883003dbda932cf7fdd9e61714077ba057bf0f2 checked=2026-11-23 -->

- **上游仓库**：https://github.com/simonlin1212/a-stock-data（原作者 Simon 林，默认分支 `main`）
- **本地基线与版本**：本地派生自上游 **V3.1**（7 层 28 端点）；当前本地版本 `metadata.version: '3.2.0'`（`source: third-party-adapted`）。
- **2026-11-23 上游巡检实况**：
  - `https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/SKILL.md` 可达（HTTP 200，长度 442,341 字节，sha256 `09f7e8a3f826f747d293a1e86883003dbda932cf7fdd9e61714077ba057bf0f2`，仓库 `pushed_at: 2026-11-03T23:52:13Z`）。
  - 上游已演进至 **V3.10.4**（15 层 87 端点、单文件 ~442KB）。本次仅建档留存基准快照，**未直接升级合并 V3.10.4**（避免 442KB 单文件膨胀并防止冲掉本地契约修复；如后续需要其中新增数据源，应按需局部摘取并做独立审查与测试）。
  - 机器可读检查注释记录当前已审上游快照（`version=3.10.4` + 对应 `sha256`），用于后续 `skills-check.sh` 追踪上游在 2026-11-23 之后的增量变化。

## 本地改动与契约修复（升级时必须保留）

1. **2026-11-16 本地契约修复（本地版本 3.1.1）**：
   - `tencent_quote`：支持显式前缀/后缀与裸 6 位输入并严格区分同码股票与指数（如 `000001` 始终指 `sz000001`，不覆写 `sh000001`），非法代码直接抛 `ValueError` 不发请求。
   - `dragon_tiger_board`：空榜时避免多发无意义席位查询并返回结构化空结果。
   - `ths_eps_forecast`：要求明确含 `每股收益`/`EPS` 表头与唯一 `年度`/`预测机构数`/`均值` 列，拒绝任意首表冒充 EPS，歧义列 fail-closed。
   - `forward_pe` / `pe_digestion` / `calc_peg` / `full_valuation`：显式按 `forecast_year` 定位均值而非最小值或行序；高 PE 无增长标记为 `不可消化` 而非 0 年；缺失/非法 EPS 保持 `未计算` 与 `forecast_error`，不将缺数当零增长。
   - `hsgt_realtime`：明确东财北向 2024-08 后上游断供背景，实时函数仅读取不自动落盘，保存须先核交易日与字段语义。
   - 配套离线回归测试：`tests/test_markdown_functions.py`、`tests/test_valuation_contract.py`。
2. **2026-11-23 渐进式披露拆瘦（本地版本 3.2.0）**：
   - 主 `SKILL.md` 瘦身至 ~115 行，保留依赖、全局 helper（`get_prefix`、`eastmoney_datacenter`、Ticker 归一化）与 7 层 28 端点路由表。
   - 7 层全部原始代码、字段速查表、估值公式、调研流程与 FAQ 100% 完整拆分至 `references/layer1-quote.md` 至 `references/layer7-announcements.md` 与 `references/workflows-and-faq.md`。
   - `tests/test_markdown_functions.py` 适配多文件代码提取并新增结构校验测试。

## 后续局部升级步骤

1. 先备份本目录原件，拉取上游 `SKILL.md` 到临时目录对比目标端点，**不要覆盖本目录或直接替换为单文件**。
2. 仅摘取确有需要的新端点到对应 `references/` 模块，并在 `SKILL.md` 路由表登记。
3. 保留上述 11-16 全部契约修复，运行 `tests/` 离线单测与 `quick_validate.py` 验收后再更新本档案哈希与日期。
