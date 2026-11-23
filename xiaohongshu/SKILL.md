---
name: xiaohongshu
description: 小红书内容抓取 — 关键词搜索、笔记详情+评论、用户主页+笔记列表。依赖 web-access Chrome CDP 复用日常浏览器登录态。触发：小红书、红书、xhs、rednote、xiaohongshu
license: MIT
metadata:
  version: 2.0.0
  created: '2026-06-13'
  last_modified: '2026-11-23'
  requires: web-access
  skill-author: 指挥官
  category: infra
  source: self-built
---

# 小红书内容抓取

> 通过 `web-access` Chrome CDP Proxy 复用日常浏览器的真实登录态访问小红书，从 Vue SSR 状态 (`window.__INITIAL_STATE__`) 直接提取结构化数据，比纯 DOM 拼接解析更稳健高效。

## 三种操作模式

| 模式 | 输入 | 输出 | 脚本 |
|------|------|------|------|
| **搜索** | 关键词 | 笔记列表（标题/作者/赞/收藏/评论） | `extract-search.py` |
| **笔记详情** | note_id + xsecToken | 笔记正文+元数据+评论 | `extract-note-detail.py` + `extract-note-comments.py` |
| **用户主页** | user_id | 用户信息+发布笔记列表 | `extract-user-profile.py` + `extract-user-notes.py` |

## 前置条件

- Node.js 22+（`web-access` CDP Proxy 依赖原生 WebSocket）
- 已安装 `web-access` 技能（真源：`/Users/sishuai/Documents/My_Skills_Library/社区第三方/web-access`），且日常 Chromium 内核浏览器（Chrome / Edge / Dia / Arc / Brave 等）已开启远程调试并完成 `web-access` 首次配置
- 日常浏览器中已登录小红书（CDP 直连日常浏览器，天然复用登录态；如未登录，在浏览器完成登录后刷新页面继续）
- 在执行站内操作前，按 `web-access` 约定直接向用户展示以下须知：

```text
温馨提示：部分站点对浏览器自动化操作检测严格，存在账号封禁风险。已内置防护措施但无法完全避免，Agent 继续操作即视为接受。
```

## 工具就绪检查

优先从当前宿主加载的 `web-access` `SKILL.md` 解析脚本真源目录；未显式提供时回退到本机真源目录，不硬编码宿主专属路径：

```bash
WEB_ACCESS_SKILL_ROOT="${WEB_ACCESS_SKILL_ROOT:-$(python3 -c '
from pathlib import Path
import os, sys
raw = os.environ.get("WEB_ACCESS_SKILL_MD")
if raw and Path(raw).exists():
    p = Path(raw).resolve()
    print(p.parent if p.is_file() else p)
else:
    fallback = Path("/Users/sishuai/Documents/My_Skills_Library/社区第三方/web-access")
    if not (fallback / "scripts/check-deps.mjs").is_file():
        sys.exit("未找到 web-access 技能根目录，请设置 WEB_ACCESS_SKILL_MD 或 WEB_ACCESS_SKILL_ROOT")
    print(fallback.resolve())
')}"

# 检查并复用/启动共享 CDP Proxy（默认端口 3456）
node "$WEB_ACCESS_SKILL_ROOT/scripts/check-deps.mjs"
# exit 0 -> 直接调用 Proxy API（不手动重启 Proxy）
# exit 2 -> 尚未配置浏览器，按 check-deps.mjs 输出完成首次配置
# exit 1 -> 按 stdout 中的「Agent 处理顺序」排查；仍失败再向用户求助
```

如需复核连接态，可调用 `curl -sS "http://localhost:${CDP_PROXY_PORT:-3456}/health"`，确认 `status == "ok"` 且 `connected == true`。

## 提取命令初始化

先将当前实际加载的 `xiaohongshu` `SKILL.md` 路径（通过环境变量 `XHS_SKILL_MD` 传入）解析为绝对真源目录；未显式提供时回退到本机真源目录 `/Users/sishuai/Documents/My_Skills_Library/技能库_自建/xiaohongshu`，不按当前工作目录找 `scripts/`，也不硬编码任何宿主配置目录。在执行提取的同一 shell 中先定义以下函数：

```bash
XHS_SKILL_ROOT="${XHS_SKILL_ROOT:-$(python3 -c '
from pathlib import Path
import os, sys
raw = os.environ.get("XHS_SKILL_MD")
if raw and Path(raw).exists():
    p = Path(raw).resolve()
    print(p.parent if p.is_file() else p)
else:
    fallback = Path("/Users/sishuai/Documents/My_Skills_Library/技能库_自建/xiaohongshu")
    if not (fallback / "scripts").is_dir():
        sys.exit("未找到 xiaohongshu 技能根目录，请设置 XHS_SKILL_MD 或 XHS_SKILL_ROOT")
    print(fallback.resolve())
')}"
XHS_CDP_PROXY="${XHS_CDP_PROXY:-http://localhost:${CDP_PROXY_PORT:-3456}}"
XHS_TARGET_ID="${XHS_TARGET_ID:-}"
XHS_TARGET_OWNED="${XHS_TARGET_OWNED:-0}"

xhs_open_tab() {
  local url="${1:-https://www.xiaohongshu.com}" resp tid
  resp="$(curl -sS -X POST --data-raw "$url" "${XHS_CDP_PROXY}/new")" || return 1
  tid="$(printf '%s' "$resp" | python3 -c 'import json,sys
d = json.load(sys.stdin)
tid = d.get("targetId") if isinstance(d, dict) else None
if not tid:
    print(json.dumps(d, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)
print(tid)')" || return 1
  XHS_TARGET_ID="$tid"
  XHS_TARGET_OWNED=1
  printf '%s\n' "$XHS_TARGET_ID"
}

xhs_navigate() {
  local url="${1:?需要目标 URL}"
  if [[ -z "${XHS_TARGET_ID:-}" ]]; then
    printf '%s\n' '未初始化 XHS_TARGET_ID；请先调用 xhs_open_tab 创建本次任务专属 tab' >&2
    return 1
  fi
  curl -sS --fail-with-body -X POST --data-raw "$url" "${XHS_CDP_PROXY}/navigate?target=${XHS_TARGET_ID}"
}

xhs_scroll() {
  local y="${1:-3000}" direction="${2:-down}"
  if [[ -z "${XHS_TARGET_ID:-}" ]]; then
    printf '%s\n' '未初始化 XHS_TARGET_ID；请先调用 xhs_open_tab 创建本次任务专属 tab' >&2
    return 1
  fi
  curl -sS --fail-with-body "${XHS_CDP_PROXY}/scroll?target=${XHS_TARGET_ID}&y=${y}&direction=${direction}"
}

xhs_extract() {
  local script="${1:?需要提取脚本名}" js resp
  shift
  if [[ -z "${XHS_TARGET_ID:-}" ]]; then
    printf '%s\n' '未初始化 XHS_TARGET_ID；请先调用 xhs_open_tab 创建本次任务专属 tab' >&2
    return 1
  fi
  js="$(python3 "$XHS_SKILL_ROOT/scripts/$script" "$@")" || return
  if [[ -z "${js//[[:space:]]/}" ]]; then
    printf '%s\n' '提取脚本未生成 JavaScript；不调用浏览器' >&2
    return 1
  fi
  resp="$(printf '%s' "$js" | curl -sS -X POST "${XHS_CDP_PROXY}/eval?target=${XHS_TARGET_ID}" --data-binary @-)" || return
  printf '%s' "$resp" | python3 -c 'import json,sys
d = json.load(sys.stdin)
if isinstance(d, dict) and "error" in d:
    print(json.dumps(d, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)
val = d.get("value", d) if isinstance(d, dict) else d
print(val if isinstance(val, str) else json.dumps(val, ensure_ascii=False))'
}

xhs_close_tab() {
  if [[ "${XHS_TARGET_OWNED:-0}" = 1 && -n "${XHS_TARGET_ID:-}" ]]; then
    curl -sS "${XHS_CDP_PROXY}/close?target=${XHS_TARGET_ID}" >/dev/null
    XHS_TARGET_ID=""
    XHS_TARGET_OWNED=0
  fi
}
```

安全与协议边界：
- 提取脚本只打印 JavaScript，不自行访问网页；通过 `curl --data-binary @-` 将 JS 原样走 stdin POST 给 `POST /eval?target=$XHS_TARGET_ID`（保留换行与注释，避免 `curl -d` 吞换行破坏 JS）。**严禁把 JS 交给 shell 的 `eval` 执行**。
- 脚本失败或空输出必须立即停止，绝不能把空输出解释为“无笔记”。
- `/new` 与 `/navigate` 一律按 `web-access` v2.5.3+ 协议用 `POST --data-raw "$url"` 传完整 URL，避免含 `&`、`xsec_token` 的查询串被切分。

## 创建专属标签页与登录检查

不借用、不操作用户已有 tab；始终通过 `/new` 创建本次任务专属后台 tab，成功返回 `targetId` 后才标记 `XHS_TARGET_OWNED=1`：

```bash
# 1. 创建本次任务专属后台 tab
xhs_open_tab "https://www.xiaohongshu.com" || exit 1

# 2. 检查页面信息与加载/登录状态（/new 返回仅保证基础文档加载，不代表业务数据就绪）
curl -sS "${XHS_CDP_PROXY}/info?target=${XHS_TARGET_ID}"
curl -sS -X POST "${XHS_CDP_PROXY}/eval?target=${XHS_TARGET_ID}" --data-binary @- <<'EOF'
JSON.stringify({
  url: location.href,
  title: document.title,
  hasInitialState: Boolean(window.__INITIAL_STATE__),
  hasLoginModal: Boolean(document.querySelector('[class*="login-modal"], [class*="qrcode"], .login-container'))
})
EOF
```

判断规则：
- 页面中出现“我”等文本不充分证明已登录；以目标 `__INITIAL_STATE__` 数据可读且未被登录墙/扫码弹窗/验证页阻断为准。
- `/new` 或 `/navigate` 后若目标数据尚未出现，在默认 15 秒窗口内轮询 `/eval` 观察页面状态变化，不要盲目把首次空态判为无结果。
- 确认登录阻断目标内容时，告知用户在日常浏览器中登录小红书，完成后通知继续；登录完成后无需重启 Proxy，直接用 `xhs_navigate` 重新加载目标页即可。

---

## 模式一：关键词搜索

```text
URL: https://www.xiaohongshu.com/search_result/?keyword={keyword}
提取源: window.__INITIAL_STATE__.search.feeds
```

### 工作流

```bash
# 1. 导航到搜索结果页（中文关键词建议先做 URL 编码）
xhs_navigate "https://www.xiaohongshu.com/search_result/?keyword={关键词}"

# 2. 确认 window.__INITIAL_STATE__.search.feeds 就绪后，提取当前累计列表的首段
xhs_extract extract-search.py --offset 0 --limit 20
```

### 输出格式

```json
{
  "total": 44,
  "offset": 0, "returned": 20, "nextOffset": 20,
  "hasMore": true,
  "items": [{
    "id": "...", "xsecToken": "...", "type": "normal",
    "title": "...", "userId": "...", "nickname": "...",
    "likedCount": "5149", "collectedCount": "4170", "commentCount": "390",
    "coverUrl": "..."
  }]
}
```

### 可选：排序和类型筛选

在提取前通过页面筛选面板操作：

| 排序 | 值 | 类型 | 值 |
|------|-----|------|-----|
| 综合(默认) | general | 全部(默认) | — |
| 最新 | time_descending | 视频 | video-note |
| 最热 | popularity_descending | 图文 | image-text-note |
| 最多评论 | comment_descending | | |
| 最多收藏 | collect_descending | | |

操作流程：用 `/eval` 检查筛选按钮与选项选择器 → `POST /click?target=$XHS_TARGET_ID`（或 `/clickAt`）展开并点击对应筛选项 → 等待列表刷新完成 → 从 `--offset 0` 重新提取。

### 翻页

```bash
# nextOffset < total 时先读已加载但未输出的下一段，无需先滚动。
xhs_extract extract-search.py --offset 20 --limit 20  # 20 替换为上一轮 nextOffset

# 已读取完当前 total 且 hasMore 为 true 时，滚动加载再从上轮 nextOffset 继续。
xhs_scroll 3000 down
# /scroll 默认等待 800ms 触发懒加载；如需确认新条目已入列，可用 /eval 复核 feeds.length。
# 每轮按 id 去重；若排序/过滤重置列表，从 offset 0 重新读取。
# 仅 hasMore=false 且 nextOffset>=total 才说明已消费当前加载列表；不保证源站全量。
# 连续无新增或状态未知时停止并报覆盖缺口，不无限滚动。
```

---

## 模式二：笔记详情

```text
URL: https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsecToken}&xsec_source=pc_search
提取源: window.__INITIAL_STATE__.note.noteDetailMap
```

### 工作流

```bash
# 1. 导航到笔记页（保留搜索结果中的完整 note_id 与 xsecToken；URL 走 POST body 不被切分）
xhs_navigate "https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsecToken}&xsec_source=pc_search"

# 2. 确认 window.__INITIAL_STATE__.note.noteDetailMap 就绪后，提取笔记详情
xhs_extract extract-note-detail.py "{note_id}"

# 3. 提取初始评论
xhs_extract extract-note-comments.py "{note_id}"
```

### 输出格式（笔记详情）

```json
{
  "noteId": "...", "title": "...", "desc": "...",
  "type": "normal", "time": 1748390400000, "ipLocation": "Fujian",
  "userId": "...", "nickname": "...", "avatar": "...",
  "likedCount": "5149", "collectedCount": "4170", "commentCount": "390",
  "shareCount": "112", "tagList": [{"name": "travel", "type": "topic"}],
  "imageCount": 9
}
```

### 输出格式（评论）

```json
{
  "count": 10, "cursor": "...", "hasMore": true,
  "comments": [{
    "id": "...", "content": "...", "likeCount": "23",
    "createTime": 1748390500000, "ipLocation": "Guangdong",
    "userId": "...", "nickname": "...", "avatar": "..."
  }]
}
```

### 评论翻页

每次调用 `xhs_scroll 3000 down`（若评论位于独立滚动容器内，用 `/eval` 滚动对应容器）触发加载更多评论后，重新运行 `extract-note-comments.py` 获取累计列表并按评论 `id` 去重；当 `hasMore=false` 或连续无新增时停止，不无限滚动。

---

## 模式三：用户主页

```text
URL: https://www.xiaohongshu.com/user/profile/{user_id}
提取源: window.__INITIAL_STATE__.user.userPageData
```

### 工作流

```bash
# 1. 导航到用户主页
xhs_navigate "https://www.xiaohongshu.com/user/profile/{user_id}"

# 2. 确认 window.__INITIAL_STATE__.user.userPageData 就绪后，提取用户资料
xhs_extract extract-user-profile.py "{user_id}"

# 3. 提取用户笔记列表
xhs_extract extract-user-notes.py --limit 30
```

### 输出格式（用户资料）

```json
{
  "userId": "...", "nickname": "...", "desc": "...",
  "gender": 1, "ipLocation": "Shanghai", "avatar": "...",
  "follows": "361", "fans": "23904", "interaction": "1086463",
  "tags": ["travel", "food"]
}
```

### 输出格式（用户笔记）

```json
{
  "total": 24, "hasMore": false,
  "notes": [{
    "type": "normal", "title": "...",
    "likedCount": "5149", "collectedCount": "4170", "commentCount": "390",
    "coverUrl": "..."
  }]
}
```

---

## 已知限制与反爬提示

- 所有操作需登录；未登录时 `__INITIAL_STATE__` 为空或被登录弹窗阻断
- `xsecToken` 必须匹配 `note_id`，且优先保留站内自然观察到的完整 URL 参数，不要自行伪造 token，否则易被重定向或误判内容不存在
- 用户笔记列表的 `id` 始终为 `null`，需通过搜索结果或点击卡片观察真实链接获取 `note_id`
- 图片实际 URL 未在 `extract-note-detail.py` 中提取，仅返回 `imageCount`；如需读取图片 URL，可通过 `/eval` 定向检查 `imageList` 或页面 DOM
- **并发反爬提示**：短时间内密集 `/new` 或对小红书高并发抓取易触发风控/验证码；单个任务优先复用同一专属 `XHS_TARGET_ID` 串行导航，确需多任务并行时控制节奏，且每个任务独立管理自己的 `targetId`
- 本技能仅用于只读内容抓取与调研，不授权点赞、收藏、关注、私信、评论发送或发布笔记

## 标签页与 Proxy 管理

- **仅关闭自己新建的标签页**：任务结束执行 `xhs_close_tab`（仅在 `XHS_TARGET_OWNED = 1` 且 `XHS_TARGET_ID` 非空时调用 `GET /close?target=$XHS_TARGET_ID`）。**绝不关闭用户已有标签页**，也不得操作未归属本次任务的 tab；若跨 shell 接续，先通过 `GET /targets` 核实原 tab 归属，不能重新造变量冒充归属。
- **保持共享 Proxy 常驻**：CDP Proxy 为全体 Agent 共享长驻服务，普通任务结束后不停止或重启 Proxy；下次任务先跑 `check-deps.mjs` 复用连接即可。
- **登录态过期处理**：长期不用导致小红书登录态过期时，由用户在日常浏览器重新登录后刷新继续，无需重建浏览器实例。
