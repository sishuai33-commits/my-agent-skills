---
name: xiaohongshu
description: 小红书内容抓取 — 关键词搜索、笔记详情+评论、用户主页+笔记列表。依赖 browser-act stealth 浏览器。触发：小红书、红书、xhs、rednote、xiaohongshu
metadata:
  version: 1.0.0
  created: '2026-06-13'
  requires: browser-act
  last_modified: '2026-06-13'
  skill-author: 指挥官
category: infra
source: self-built
license: MIT
---


# 小红书内容抓取

> 通过 browser-act stealth 浏览器访问小红书，从 Vue SSR 状态 (`window.__INITIAL_STATE__`) 直接提取结构化数据。比 DOM 解析高效得多。

## 三种操作模式

| 模式 | 输入 | 输出 | 脚本 |
|------|------|------|------|
| **搜索** | 关键词 | 笔记列表（标题/作者/赞/收藏/评论） | `extract-search.py` |
| **笔记详情** | note_id + xsecToken | 笔记正文+元数据+评论 | `extract-note-detail.py` + `extract-note-comments.py` |
| **用户主页** | user_id | 用户信息+发布笔记列表 | `extract-user-profile.py` + `extract-user-notes.py` |

## 前置条件

- browser-act 已安装：`uv tool install browser-act-cli --python 3.12`
- stealth 浏览器已创建：`browser-act browser create --name "xhs" --type stealth --desc "小红书抓取"`
- 已登录小红书（首次需 headed 模式扫码登录，后续登录态持久保留）

## 工具就绪检查

```bash
# 检查 browser-act 是否可用
browser-act --help > /dev/null 2>&1 || { echo "browser-act 未安装"; exit 1; }

# 检查浏览器是否存在
browser-act browser list | grep -q xhs || {
  echo "stealth 浏览器不存在，创建中..."
  browser-act browser create --name "xhs" --type stealth --desc "小红书抓取"
}
```

## 提取命令初始化

先将本次实际加载的 `SKILL.md` 路径解析为绝对真源目录；下面以本机发现入口为例，其他入口替换该参数，不按当前工作目录找 `scripts/`。在执行提取的同一 shell 中先定义函数：

```bash
XHS_SKILL_ROOT="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve().parent)' "$HOME/.claude/skills/xiaohongshu/SKILL.md")"
xhs_extract() {
  local script="${1:?需要提取脚本名}" js
  shift
  js="$(python3 "$XHS_SKILL_ROOT/scripts/$script" "$@")" || return
  if [[ -z "${js//[[:space:]]/}" ]]; then
    printf '%s\n' '提取脚本未生成 JavaScript；不调用浏览器' >&2
    return 1
  fi
  browser-act --session xhs eval "$js"
}
```

提取脚本只打印 JavaScript，不自行访问网页。本机 browser-act 随包 `guide/baseline/references/core-commands.md` 定义的接口是 `browser-act --session <name> eval "JavaScript"`；**不能把 JS 交给 shell 的 `eval`**。脚本失败或空输出必须停止，不能把空输出解释为无笔记。

## 登录检查

```bash
# 打开小红书首页，检查登录状态
browser-act --session xhs browser open <browser_id> "https://www.xiaohongshu.com"
browser-act --session xhs wait stable
browser-act --session xhs state | grep -q "我" || {
  echo "未登录，需要 headed 模式登录："
  echo "browser-act --session xhs browser open <browser_id> 'https://www.xiaohongshu.com' --headed"
  exit 1
}
```

---

## 模式一：关键词搜索

```
URL: https://www.xiaohongshu.com/search_result/?keyword={keyword}
提取源: window.__INITIAL_STATE__.search.feeds
```

### 工作流

```bash
# 1. 导航到搜索结果页
browser-act --session xhs navigate "https://www.xiaohongshu.com/search_result/?keyword={关键词}"

# 2. 等待页面稳定
browser-act --session xhs wait stable

# 3. 提取结果
xhs_extract extract-search.py --limit 20
```

### 输出格式

```json
{
  "total": 44,
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

在提取前通过 filter 面板操作：

| 排序 | 值 | 类型 | 值 |
|------|-----|------|-----|
| 综合(默认) | general | 全部(默认) | — |
| 最新 | time_descending | 视频 | video-note |
| 最热 | popularity_descending | 图文 | image-text-note |
| 最多评论 | comment_descending | | |
| 最多收藏 | collect_descending | | |

操作流程：`state` → 找到筛选按钮 → `click` → `state` 选筛选项 → `click` → 收起面板 → `wait stable` → 提取

### 翻页

```bash
browser-act --session xhs scroll down --amount 3000
browser-act --session xhs wait stable
xhs_extract extract-search.py --limit 20
# 当 hasMore: false 时停止
```

---

## 模式二：笔记详情

```
URL: https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsecToken}&xsec_source=pc_search
提取源: window.__INITIAL_STATE__.note.noteDetailMap
```

### 工作流

```bash
# 1. 导航到笔记页（需要搜索结果中的 id 和 xsecToken）
browser-act --session xhs navigate "https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsecToken}&xsec_source=pc_search"

# 2. 等待页面稳定
browser-act --session xhs wait stable

# 3. 提取笔记详情
xhs_extract extract-note-detail.py "{note_id}"

# 4. 提取初始评论
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

每次 scroll 加载更多评论，重新运行 `extract-note-comments.py` 获取累计列表。

---

## 模式三：用户主页

```
URL: https://www.xiaohongshu.com/user/profile/{user_id}
提取源: window.__INITIAL_STATE__.user.userPageData
```

### 工作流

```bash
# 1. 导航到用户主页
browser-act --session xhs navigate "https://www.xiaohongshu.com/user/profile/{user_id}"

# 2. 等待页面稳定
browser-act --session xhs wait stable

# 3. 提取用户资料
xhs_extract extract-user-profile.py "{user_id}"

# 4. 提取用户笔记列表
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

## 已知限制

- 所有操作需登录；未登录时 `__INITIAL_STATE__` 为空
- xsecToken 必须匹配 note_id，否则被重定向
- 用户笔记列表的 `id` 始终为 null，需通过搜索获取 note_id
- 图片实际 URL 未提取，仅返回 `imageCount`
- 同一浏览器内不要并行操作（触发反爬），多任务用多个 stealth 浏览器并行

## 会话管理

- 完成任务后关闭会话释放资源：`browser-act session close xhs`
- 不使用时浏览器保持 idle 状态，下次直接 reopen 即可，无需重新登录
- 长期不用登录态可能过期，需重新 headed 登录

## 浏览器配置

```bash
# 当前已创建的浏览器
browser-act browser list

# 查看浏览器详情
browser-act browser list  # 记下 xhs 浏览器的 ID

# 删除旧浏览器（如需重建）
browser-act browser delete <id>
```
