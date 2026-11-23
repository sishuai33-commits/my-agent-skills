---
name: xiaohongshu
description: 读取小红书搜索结果、笔记正文与评论、用户主页及笔记列表；通过 web-access Chrome CDP 复用日常浏览器登录态并保留可追溯链接。内容调研使用，发布、点赞、关注和评论发送不在本技能范围。
metadata:
  source_path: /Users/sishuai/Documents/My_Skills_Library/技能库_自建/xiaohongshu
  adapted_for: Codex
  source_version: '2.0.0'
  adapted_on: '2026-11-23'
  requires: web-access
---

# 小红书读取

将自建 `xiaohongshu` 技能（v2.0.0）适配到 Codex，统一通过 `web-access` Chrome CDP Proxy 复用日常浏览器登录态读取小红书内容。

## 路径解析与前置就绪

不硬编码任何宿主技能目录；优先解析当前加载的 `SKILL.md` 真源路径，未显式提供时回退到本机真源目录：

- `xiaohongshu` 真源：`/Users/sishuai/Documents/My_Skills_Library/技能库_自建/xiaohongshu`（5 个提取脚本位于其 `scripts/` 下）
- `web-access` 真源：`/Users/sishuai/Documents/My_Skills_Library/社区第三方/web-access`

开始站内操作前：
1. 运行 `node "$WEB_ACCESS_SKILL_ROOT/scripts/check-deps.mjs"` 确认共享 CDP Proxy（默认 `http://localhost:3456`）连接就绪；`exit 0` 直接复用，不重启共享 Proxy。
2. 向用户展示 `web-access` 自动化风险提示（存在账号封禁风险，继续操作即视为接受）。
3. 通过 `POST /new`（URL 放 POST body）创建本次任务专属后台 tab 并记录 `XHS_TARGET_ID` 与 `XHS_TARGET_OWNED=1`；不操作用户已有 tab。

## 三类请求与提取规则

| 输入 | 工作与输出 |
|---|---|
| 搜索关键词 | `POST /navigate?target=ID` 进入搜索页（需要排序/类型筛选时用 `/eval` + `/click` 操作真实筛选控件），调用 `extract-search.py` 通过 `POST /eval` 提取标题、作者、互动量、`note_id` 与 `xsecToken` |
| 笔记 URL / `note_id` + `xsecToken` | 保留站内观察到的完整 URL 参数并用 `POST /navigate?target=ID` 打开，调用 `extract-note-detail.py` 与 `extract-note-comments.py` 读取正文、标签与评论，记录实际读取数与 `hasMore` |
| 用户主页 URL / `user_id` | 导航到用户主页后调用 `extract-user-profile.py` 与 `extract-user-notes.py` 读取公开资料与已加载笔记列表（用户笔记 `id` 恒为 `null`，需结合搜索或真实卡片链接定位笔记详情） |

## 协议与安全边界

- **禁止 shell `eval`**：5 个 `extract-*.py` 仅生成 JS 表达式；统一通过 `curl -sS -X POST "$XHS_CDP_PROXY/eval?target=$XHS_TARGET_ID" --data-binary @-` 走 stdin 发送给 CDP Proxy 并解包返回 JSON 的 `value` 字段。脚本报错或输出为空时立即停止，不把空输出当作无结果。
- **保留完整 URL 参数**：小红书链接依赖 `xsec_token` 等上下文参数，一律走 POST body 传给 `/new` 与 `/navigate`，不得裁剪参数或根据 `note_id` 自造 token；遇到重定向先回到站内导航核实，持续受限则如实报告。
- **数据就绪与回退**：`/new` 与 `/navigate` 返回不代表 `window.__INITIAL_STATE__` 已就绪，需在 15 秒观察窗口内确认目标状态；若页面结构变更导致状态提取不可用，改用 `/eval` 读取可见 DOM，不编造字段。
- **翻页与防风控**：滚动使用 `GET /scroll?target=ID&y=3000&direction=down`，按笔记/评论唯一 `id` 去重并记录已输出数与已加载数；**不得把 `hasMore=false` 或停止滚动直接等同于全量结果**，连续无新增即停止并注明覆盖缺口。控制频率，避免高并发短时批量 `/new` 触发反爬。
- **登录、清理与只读范围**：如登录确实阻断目标，请用户在日常浏览器完成登录后刷新继续；任务结束**仅关闭本次新建的 `targetId`**（`GET /close?target=ID`），绝不关闭用户已有 tab，也不停止共享 Proxy。读取请求不授权点赞、收藏、关注、私信、发评论或发布笔记。

结果区分作者陈述、评论观点与助手推断；互动量保留原始单位与采集时点，无来源链接或不可见字段如实注明缺口。
