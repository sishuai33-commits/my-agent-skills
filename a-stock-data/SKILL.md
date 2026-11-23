---
name: a-stock-data
description: A股全栈数据工具包 — 覆盖行情(mootdx+腾讯+百度K线)、研报(东财+同花顺+iwencai)、信号(同花顺热点+北向+龙虎榜+解禁+行业)、资金面(融资融券+大宗交易+股东户数+分红+资金流分钟级+资金流120日)、新闻(东财+财联社)、基础数据(mootdx财务/F10+东财+新浪三表)、公告(巨潮)七层28个直连端点。适用于个股估值、研报检索、题材归因、龙虎榜跟踪、解禁预警、行业轮动、融资融券、筹码分析、产业链调研、批量筛选等需要代码取数的场景；纯概念解释或策略讨论无需加载。
license: MIT
metadata:
  category: analysis
  source: third-party-adapted
  upstream: https://github.com/simonlin1212/a-stock-data
  version: '3.2.0'
  last_modified: '2026-11-23'
  skill-author: 指挥官
---

# A股全栈数据工具包（V3.2 本地拆瘦版）

> 上游基线：https://github.com/simonlin1212/a-stock-data（原作者 Simon 林，本地基于 V3.1 适配并叠加 2026-11-16 估值/行情/龙虎榜契约修复与 2026-11-23 按需拆分；上游追踪与差异见 `UPSTREAM.md`）。

七层数据架构、28 个直连端点（覆盖主板/中小板/科创板/ST）；除 `mootdx` 保留 TCP 7709 外，全部直连 HTTP API，无 `akshare` 依赖。实时可用性与字段结构须在当次调用时核验。

## 依赖与鉴权

```bash
pip install mootdx requests pandas stockstats
```

| 依赖 | 要求 | 用途 |
|------|------|------|
| `mootdx` | `>= 0.10` | TCP 行情 + 37 字段财务快照 + F10（唯一非 HTTP 依赖） |
| `requests` / `pandas` / `stockstats` | any | HTTP API 直连 / 表格解析 / 技术指标 |

- **仅 iwencai 语义搜索需要 Key**（申请：https://www.iwencai.com/skillhub，且必须携带 SkillHub 2.0 `X-Claw-*` Headers，详见 `references/layer2-research.md`）：
  ```bash
  export IWENCAI_API_KEY="your_key_here"
  export IWENCAI_BASE_URL="https://openapi.iwencai.com"
  ```
- 其余数据源（mootdx / 腾讯 / 东财 / 同花顺 / 百度股市通 / 新浪 / 巨潮 / 财联社）均免费无 Key。

## 全局通用规则

### 市场前缀规则

```python
def get_prefix(code: str) -> str:
    """6位代码 → 市场前缀"""
    if code.startswith(("6", "9")):
        return "sh"
    elif code.startswith("8"):
        return "bj"
    else:
        return "sz"
```

### Ticker 格式归一化

`tencent_quote`（见 `references/layer1-quote.md`）支持显式前后缀（`SH688017` / `688017.SH` / `sh000001` / `SZ000001` / `BJ832000`）及裸 6 位代码，并严格保留股票与指数的交易所身份（如 `000001` 始终指 `sz000001`，指数须显式传 `sh000001`）。其余代码段默认要求**纯 6 位证券代码**，调用前须显式归一化，不保证内部剥离前后缀。

### 东财数据中心统一查询（共用 helper）

龙虎榜 / 解禁 / 融资融券 / 大宗交易 / 股东户数 / 分红均复用以下常量与函数：

```python
import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

def eastmoney_datacenter(report_name: str, columns: str = "ALL",
                          filter_str: str = "", page_size: int = 50,
                          sort_columns: str = "", sort_types: str = "-1") -> list[dict]:
    """东财数据中心统一查询 — 龙虎榜/解禁/融资融券/大宗交易/股东户数/分红 共用"""
    params = {
        "reportName": report_name, "columns": columns,
        "filter": filter_str, "pageNumber": "1", "pageSize": str(page_size),
        "sortColumns": sort_columns, "sortTypes": sort_types,
        "source": "WEB", "client": "WEB",
    }
    r = requests.get(DATACENTER_URL, params=params, headers={"User-Agent": UA}, timeout=15)
    d = r.json()
    if d.get("result") and d["result"].get("data"):
        return d["result"]["data"]
    return []
```

## 七层 28 端点按需路由索引

按任务读取对应 `references/*.md` 获取完整可运行代码、字段速查表与踩坑说明，不整包注入：

| 层级 / 场景 | 覆盖端点与核心函数 | 读取文件 |
|---|---|---|
| **Layer 1 行情层** | `mootdx`（K线/五档/逐笔）、`tencent_quote`（PE/PB/市值/涨跌停/指数/ETF + 索引校准表：43=振幅、46=PB）、`baidu_kline_with_ma`（自带MA5/10/20） | `references/layer1-quote.md` |
| **Layer 2 研报层** | `eastmoney_reports` + `download_pdf`（研报列表/PDF）、`ths_eps_forecast`（同花顺一致预期EPS，显式表头校验）、`iwencai_search` / `iwencai_query` / `dedup_articles`（NL语义搜研报） | `references/layer2-research.md` |
| **Layer 3 信号层** | `ths_hot_reason`（强势股+题材归因）、`hsgt_realtime` + 本地自缓存（北向分钟流向）、`baidu_concept_blocks`（概念归属）、`eastmoney_fund_flow_minute`（分钟资金流）、`dragon_tiger_board`（个股龙虎榜/席位/机构）、`lockup_expiry`（限售解禁）、`industry_comparison`（行业排名）、`daily_dragon_tiger`（全市场龙虎榜）+ 信号组合 | `references/layer3-signals.md` |
| **Layer 4 资金面/筹码层** | `margin_trading`（融资融券）、`block_trade`（大宗交易）、`holder_num_change`（股东户数变化）、`dividend_history`（分红送转）、`stock_fund_flow_120d`（120日个股资金流） | `references/layer4-capital-chips.md` |
| **Layer 5 新闻层** | `eastmoney_stock_news`（东财个股新闻 JSONP）、`cls_telegraph`（财联社电报）、`eastmoney_global_news`（东财 7×24 全球资讯） | `references/layer5-news.md` |
| **Layer 6 基础数据层** | `mootdx` 37 字段季报快照、`mootdx` F10（9大类文本）、`eastmoney_stock_info`（行业/股本/市值/上市日）、`sina_financial_report`（新浪财报三表 fzb/lrb/llb） | `references/layer6-fundamentals.md` |
| **Layer 7 公告层** | `cninfo_announcements`（巨潮公告全文检索）、`mootdx` F10 最新提示摘要 | `references/layer7-announcements.md` |
| **估值公式 / 调研流程 / FAQ** | `forward_pe`、`pe_digestion`、`calc_peg`、`full_valuation`（单票/批量估值、主题研报、新标的11步调研）、数据源优先级、常见报错 FAQ 与安装说明 | `references/workflows-and-faq.md` |

## 选源与核验原则

- **优先级**：行情优先 `mootdx` + 腾讯；研报走东财 + `iwencai`；资金面走东财 `datacenter` + `push2`；信号层走同花顺 + 百度 + 东财直连。
- **契约测试**：本地离线回归测试位于 `tests/`（验证 `tencent_quote`、`dragon_tiger_board`、`ths_eps_forecast` 与估值函数契约，不依赖联网）。
