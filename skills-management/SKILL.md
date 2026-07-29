---
name: skills-management
description: Skills 全周期管理体系。新 Skills 安装评估、安全审查、版本管理、激活/禁用流程。指挥官说'安装新 skill'、'评估 skill'、'升级
  skills'时触发。
license: MIT
category: knowledge
source: self-built
metadata:
  version: 2.2.0
  last_modified: '2026-06-14'
  skill-author: 指挥官
---



# Skills 管理体系

Skills 全生命周期管理：来源评估 → 安全审查 → 版本记录 → 激活使用 → 升级维护。

**创建新 Skill → 委托 `skill-creator`（官方）**。本 skill 不负责 skill 创作（写 draft / 跑 eval / 迭代优化 / 调优触发词），这些由 Anthropic 官方 `skill-creator` 处理。skill-creator 产出后，转入本 skill 的管理流程（安全审查 → lint 门禁 → 激活）。

## 启动授权（v2.2.0 新增，PreToolUse hook 硬约束）

**每次 skills-management 启动时必须首先执行（双令牌，2026-07-26 补第二层）：**

```bash
echo $(date +%s) > /tmp/cc-skills-bypass.token    # 守卫4：SKILL.md 修改授权
echo $(date +%s) > /tmp/cc-config-bypass.token    # v1.1 重复违规层：同会话第2次同类修改放行
```

这会创建两个 5 分钟有效的授权令牌，允许本轮修改 SKILL.md 文件。`pre-security.js`（ke/tongle hook）有两层守卫：**守卫4**（SKILL.md 专门守卫）查 skills 令牌，无则拒绝任何 SKILL.md 直接写入；**v1.1 重复违规层**对同会话第 2 次同类修改 BLOCKED，只查 config 令牌。缺一会在批量编辑时卡第二层（首次仅警告放行，第 2 次硬阻断）。

---

## 一、目录架构

Skills 有两条并行路径：

### 路径 A：Skills 管理体系（手动管理）

```
~/Documents/My_Skills_Library/          # Skills 源码库（完全独立）
├── anthropic_官方/                     # Anthropic 官方 Skills
├── 技能库_自建/                        # 自建 Skills
│   ├── skills-management/              # 本 Skill
│   ├── mind-distillation/
│   └── ...
├── 社区第三方/                         # 社区/第三方 Skills
│   ├── gstack/                         # gstack 技能包
│   ├── web-access/
│   └── ...
└── 归档/                               # 不再使用的 Skills

~/.claude/skills/                       # 激活层（只有软连接）
└── [软连接...]                         # 指向 Documents 源码库
```

### 路径 B：Plugin 系统（官方自动管理）

通过 `/plugin install` 安装，由 Claude Code 内置插件系统管理：

```
~/.claude/plugins/
├── cache/<marketplace>/<plugin>/<version>/  # 插件缓存（含 skills/agents/hooks 等）
├── installed_plugins.json                   # 已安装插件清单
└── known_marketplaces.json                  # 已注册市场

~/.claude/settings.json → enabledPlugins     # 激活开关
```

**两条路径都能让 skill 生效，管理方式不同。** 详见第十六章。

---

## 二、放置规范

### 新 Skill 来源判断

| 来源关键词 | 放置目录 | 评估要求 |
|------------|----------|----------|
| "官方"、"Anthropic"、"Claude Code 原生" | `anthropic_官方/` | 信任度高，快速通过 |
| "GitHub 社区"、"第三方"、"别人开发的" | `社区第三方/` | **必须安全评估** |
| "我自己写"、"自建"、"定制" | `技能库_自建/` | 自行审查，记录意图 |

### 命名规范

- 目录名：小写 + 连字符，如 `web-access`、`mind-distillation`
- 主文件：`SKILL.md` 或 `skill.md`
- 配置文件：`config.json`、`templates/`、`references/`

---

## 三、安全评估（P0-P3 分级）

### 权限等级定义

| 等级 | 描述 | 自动通过 | 需沙箱测试 | 关键特征 |
|------|------|----------|------------|----------|
| **P0-安全** | 纯文本处理 | ✅ | ❌ | 无外部依赖，本地计算 |
| **P1-受限** | 只读访问 | ✅ | ❌ | HTTP GET、Git 读取、环境变量读取 |
| **P2-敏感** | 写入/受限执行 | ❌ | ✅ | 文件写入、网络 POST、受限命令执行 |
| **P3-高危** | 系统级操作 | ❌ | ✅ | 全局安装、任意命令、敏感目录访问 |

### 危险信号（立即拒绝）

执行安全评估时，检查以下危险模式：

```
❌ 立即拒绝：
- curl | bash 或 wget -O- | sh（远程执行）
- eval、exec 动态执行代码
- base64 --decode 后执行
- 要求 sudo 权限
- 访问 ~/.ssh、~/.aws、~/.config（敏感目录）
- 修改 /etc/ 或 shell 配置文件
- 请求密码、API 密钥输入
- 加密货币钱包路径访问

⚠️ 需要审查：
- 网络请求（API 调用）
- 文件写入操作
- 子进程执行命令
```

### 评估流程

指挥官说"评估这个 skill"时：

1. **读取 SKILL.md**：理解功能意图
2. **扫描文件**：检查危险模式
3. **判断权限等级**：P0/P1/P2/P3
4. **输出评估报告**：
   - 权限等级
   - 危险模式统计
   - 建议：批准/拒绝/需沙箱测试

---

## 四、版本管理

### Skills Registry（注册表）

每个 Skill 需在 `SKILL.md` 中记录版本信息：

```markdown
## 版本记录

| 版本 | 日期 | 来源 | 变更说明 |
|------|------|------|----------|
| v1.0.0 | 2026-03-30 | GitHub clone | 初始安装 |
| v1.1.0 | 2026-04-15 | git pull | 功能更新 |
```

### 升级记录文件

`~/Documents/My_Skills_Library/.upgrade-log.md` 记录所有升级操作：

```markdown
# Skills 升级日志

## 2026-03-30

### gstack
- 操作：git pull
- 来源：社区第三方
- 变更：新增 browse 功能优化
- 状态：✅ 成功

### web-access
- 操作：git pull
- 来源：社区第三方
- 变更：修复 CDP 连接问题
- 状态：✅ 成功
```

---

## 五、智能激活机制

### 分场景处理

| 场景 | 是否查 skill | 示例 |
|------|-------------|------|
| 简单命令 | ❌ 跳过 | ls、cat、读文件 |
| 通用编程 | ❌ 跳过 | 改代码、修 bug |
| **领域特定任务** | ✅ 必须查 | n8n 升级、报销、联网抓取 |
| **重复性任务** | ✅ 必须查 | 方法论萃取、QA 测试 |

**判断标准**：
- 涉及特定工具/平台 → 查 skill
- 有明确领域关键词 → 查 skill
- 通用操作 → 不查

### 激活流程

```
指挥官说要做某事
    ↓
判断是否需要查 skill
    ↓
需要 → 搜索源码库 → 激活 → 使用 → 删除
不需要 → 直接执行
```

### 搜索命令

```bash
# 搜索所有源码库中的 skill
find ~/Documents/My_Skills_Library -name "SKILL.md" -o -name "skill.md" | xargs grep -l "关键词"
```

### 匹配规则

| 指挥官说 | 匹配 skill | 备注 |
|----------|------------|------|
| "n8n 升级"、"n8n 版本" | n8n-docker-upgrade | 观望状态 |
| "萃取方法论"、"模拟专家思维" | mind-distillation | 如已创建 |
| "报销"、"佰钧成" | bjc-reimbursement | 如已创建 |
| "浏览网页"、"QA 测试"、"截图" | gstack | 浏览器自动化 |
| "联网"、"抓取网页"、"搜索" | web-access | 核心联网 |
| "小红书"、"红书"、"xhs"、"rednote" | xiaohongshu | 小红书抓取 |
| "飞书文档"、"飞书Doc"、"云文档" | lark-doc | ⚠️源已删(2026-05-27)，飞书文档操作需时临时激活或重建源 |
| "飞书画板"、"白板作图" | lark-whiteboard | 飞书画板 |
| "微信对话"、"微信记录" | wechat-claude-code | 微信桥接 |
| "Wiki"、"编译知识库" | wiki-management | Wiki维护 |
| "投资分析"、"加仓检查"、"投资复盘" | invest | 投资分析 |
| "IMA"、"知识库笔记" | ima-skill | IMA操作 |
| "PDF"、"合并PDF" | pdf | 文档处理 |
| "Word"、"docx文件" | docx | 文档处理 |
| "Excel"、"表格" | xlsx | 文档处理 |
| "PPT"、"演示" | pptx | 文档处理 |
| "A股"、"股票数据"、"龙虎榜"、"融资融券"、"北向资金" | a-stock-data | A股数据 |
| "/instinct-review"、"本能复审"、"校准 instinct" | instinct-review | 可临时激活，零使用 |
| "做原型"、"设计Demo"、"交互原型"、"动画Demo"、"设计变体"、"评审" | huashu-design | HTML原生设计 |
| "文章转PPT"、"杂志风PPT"、"瑞士风PPT"、"横向翻页PPT"、"guizang" | guizang-ppt-skill | 可临时激活，零使用 |
| "手绘图"、"Excalidraw图表" | excalidraw-diagram | 可临时激活 |
| "流程图"、"架构图"、"mermaid" | mermaid-visualizer | 可视化 |
| "海报"、"设计图" | canvas-design | 视觉设计 |
| "前端界面"、"网页设计"、"做网站"、"做网页"、"落地页"、"Dashboard" | frontend-design | 生产级前端（网站/组件），原型/Demo用huashu-design |
| "演示文稿"、"HTML slides" | frontend-slides | HTML演示 |
| "Claude API"、"Anthropic SDK" | claude-api | API开发 |
| "MCP服务器"、"构建MCP" | mcp-builder | MCP开发 |
| "创建技能"、"写新skill" | skill-creator | Skill创建 |

**冲突处理**：多个匹配时，按第八章优先级规则选择。

### 常驻 Skills

**常驻列表已抽到配置层（P1.3 机制vs资产分离）**：`config/skills-management/resident-skills.yaml`（knowledge-engine 项目）是单一事实源。本 SKILL.md 不硬编列表，skill 增删改只动 yaml。

**读取方式**：
```bash
KE_CONFIG="${KE_CONFIG:-$HOME/Documents/My_Code_Projects/knowledge-engine/config}"
python3 -c "
import yaml, os
d = yaml.safe_load(open('$KE_CONFIG/skills-management/resident-skills.yaml'))
print('常驻数:', d['resident_count'], '（实际统计:', sum(len(v) for v in d['resident'].values()), '）')
for cat, skills in d['resident'].items():
    print(f'  {cat}: ' + ', '.join(s['name'] for s in skills))
"
```

> 当前常驻 17 个（2026-06-24 对齐：删2幽灵 lark-doc/lark-shared 源已删 + 补6漏登 + a-stock-data 重建软连接恢复激活）。详情（分类/备注/可临时激活/已移除源）见 yaml。
> ⚠️ **纪律**：修改常驻列表时改 yaml + 实际 `ln -s`/`rm` 软链接，**不要在 SKILL.md 维护列表**——避免列表与计数不一致（历史曾 13/16 矛盾）。SKILL.md 仅保留读取说明。

### 临时激活机制

**场景**：全局链接已删除，但对话中临时需要使用该 skill。

**完整技能列表**（含已删除链接）：

| Skill | 当前状态 | 源目录 | 触发关键词 |
|-------|---------|--------|-----------|
| algorithmic-art | 已删除 | anthropic_官方 | 算法艺术、p5.js |
| brand-guidelines | 已删除 | anthropic_官方 | Anthropic 品牌 |
| slack-gif-creator | 已删除 | anthropic_官方 | Slack GIF |
| theme-factory | 已删除 | anthropic_官方 | 主题样式 |

**自动激活流程**：

```
对话中检测需求关键词
    ↓
匹配技能列表（含已删除）
    ↓
发现已删除但源文件存在
    ↓
临时创建软连接：
    ln -s ~/Documents/My_Skills_Library/<目录>/<skill> ~/.claude/skills/<skill>
    ↓
调用 Skill 工具
    ↓
使用后询问指挥官：保留链接 / 删除链接
```

**代码实现**：

```bash
# 检查技能是否存在
skill_exists() {
  ls ~/.claude/skills/$1 >/dev/null 2>&1
}

# 源文件是否存在
source_exists() {
  ls ~/Documents/My_Skills_Library/$2/$1 >/dev/null 2>&1
}

# 临时激活
temp_activate() {
  ln -s ~/Documents/My_Skills_Library/$2/$1 ~/.claude/skills/$1
}

# 清理临时链接
temp_deactivate() {
  rm ~/.claude/skills/$1
}
```

**匹配规则**（扩展）：

| 指挥官说 | 匹配 skill | 状态处理 |
|----------|------------|----------|
| "算法艺术"、"p5.js 创作" | algorithmic-art | 已删除 → 临时激活 |
| "Anthropic 品牌风格" | brand-guidelines | 已删除 → 临时激活 |
| "做个 Slack GIF" | slack-gif-creator | 已删除 → 临时激活 |
| "统一主题样式" | theme-factory | 已删除 → 临时激活 |

### 临时 Skills

- 按需激活，用完询问是否保留
- 指挥官**不需要**记住有哪些 skills
- 指挥官**不需要**手动说"激活/禁用"

---

## 六、使用评估与记录

### 使用频率统计

定期从对话记录提取使用统计（最近更新：2026-06-13）：

```
28 skill: web-access     ⭐ 核心
10 skill: xlsx
10 skill: docx
 5 skill: skills-management
 3 skill: invest
 2 skill: huashu-design
 2 skill: a-stock-data
 1 skill: wiki-management
 1 skill: pdf
 1 skill: lark-whiteboard
 0 skill: guizang-ppt-skill, wan2.7-image-skill, instinct-review, lark-doc, xiaohongshu(🆕)
```

统计命令：

```bash
grep -h "\"skill\"" ~/.claude/projects/-Users-sishuai/*.jsonl | grep -o '"skill":"[^"]*"' | sort | uniq -c | sort -rn
```

### 评估维度

| 维度 | 说明 | 评分方式 |
|------|------|----------|
| **使用频率** | 调用次数 | 从对话记录统计 |
| **效果评分** | 任务完成质量 | ★★★★★ 五级评分 |
| **触发准确度** | 自动触发是否恰当 | 高/中/低 |
| **维护状态** | 版本是否更新 | 最新/滞后/过期 |

### Skills 变更记录文件

`~/Documents/My_Skills_Library/.skills-changelog.md` 记录所有增删改：

```markdown
# Skills 变更记录

## 2026-04-18 删除无用技能
- **删除**：algorithmic-art, brand-guidelines, slack-gif-creator, theme-factory
- **原因**：使用频率 0，明确无需求
- **来源**：对话记录统计分析

## 2026-03-30 新增图表技能
- **新增**：excalidraw-diagram, mermaid-visualizer, obsidian-canvas-creator
- **来源**：社区第三方
- **用途**：符合用户可视化偏好

## 2026-04-10 新增 wiki-management
- **新增**：wiki-management
- **来源**：自建
- **用途**：Wiki 知识库全生命周期管理
```

### 定期评估流程

每季度执行一次使用评估：

1. **统计使用频率**：提取对话记录中的 Skill 调用
2. **识别低频技能**：使用次数 ≤ 2 的技能
3. **评估是否保留**：
   - 核心功能 → 保留
   - 技术储备 → 观望
   - 明确无用 → 删除
4. **更新变更记录**：记录删增操作
5. **更新常驻列表**：同步本文件常驻 Skills 列表

---

## 七、完整技能索引

### 所有可用技能列表

| Skill | 来源 | 状态 | 触发关键词 | 用途 |
|-------|------|------|-----------|------|
| **文档处理** |
| pdf | 官方 | 常驻 | PDF、pdf文件 | PDF读取/合并/提取 |
| docx | 官方 | 常驻 | Word、docx | Word文档处理 |
| xlsx | 官方 | 常驻 | Excel、xlsx、表格 | Excel处理 |
| pptx | 官方 | 可临时激活 | PowerPoint、pptx | PPT文件编辑（2026-05-26 降级） |
| **设计/原型** |
| huashu-design | 社区 | 常驻 | 做原型、设计Demo、动画、MP4、评审 | HTML原生设计（原型/幻灯片/动画/PPTX） |
| **飞书协作** |
| lark-doc | 社区 | 已删源 | 飞书文档、飞书Doc、云文档 | 飞书文档操作（2026-05-27 删源，常驻移除） |
| lark-shared | 社区 | 已删源 | — | 飞书认证/权限共享（2026-05-27 删源，常驻移除） |
| lark-whiteboard | 社区 | 常驻 | 飞书画板、白板作图 | 飞书画板（架构图/流程图首选方案） |
| **联网/抓取** |
| web-access | 社区 | 常驻 | 联网、抓取网页、搜索 | 网络访问/抓取 |
| xiaohongshu | 自建 | 常驻 | 小红书、红书、xhs、rednote | 小红书内容抓取 |
| **投资/数据** |
| invest | 自建 | 常驻 | 投资分析、加仓检查、复盘 | 投资分析框架 |
| a-stock-data | 自建 | 常驻 | A股、股票数据、龙虎榜、融资融券、北向资金 | A股全栈数据工具包 |
| **自建核心** |
| skills-management | 自建 | 常驻 | 安装skill、评估skill、升级skill | Skills全周期管理 |
| wiki-management | 自建 | 常驻 | Wiki、编译、知识库 | Wiki知识库维护 |
| **可临时激活（源文件保留）** |
| guizang-ppt-skill | 社区 | 可临时激活 | 文章转PPT、杂志风PPT、瑞士风PPT | HTML横向翻页PPT（2026-06-13 降级，零使用） |
| wan2.7-image-skill | 社区 | 可临时激活 | 图像生成、AI画图 | Wan图像生成（2026-06-13 降级，零使用） |
| instinct-review | 自建 | 可临时激活 | /instinct-review、本能复审、校准 instinct | 本能复审工具 v0.1.0（2026-06-13 降级，零使用） |
| **可临时激活（源文件保留）** |
| ima-skill | 社区 | 可临时激活 | IMA、知识库、笔记 | IMA知识库（2026-05-26 降级） |
| skill-creator | 官方 | 可临时激活 | 创建技能、写skill | 新Skill创建（2026-05-26 降级） |
| excalidraw-diagram | 社区 | 可临时激活 | 手绘图、Excalidraw | Obsidian手绘风格图表（2026-05-26 降级） |
| canvas-design | 官方 | 可临时激活 | 海报、设计图 | PNG/PDF视觉设计 |
| frontend-design | 官方 | 常驻 | 前端界面、网页设计、做网站/落地页/Dashboard | 生产级前端代码（2026-06-16 激活，与huashu-design形成Demo→生产流水线） |
| frontend-slides | 社区 | 可临时激活 | 演示文稿、slides | HTML动画演示 |
| mermaid-visualizer | 社区 | 可临时激活 | 流程图、架构图、mermaid | Mermaid可视化 |
| claude-api | 官方 | 可临时激活 | Claude API、Anthropic SDK | Claude API开发 |
| mcp-builder | 官方 | 可临时激活 | MCP服务器、MCP构建 | MCP Server开发 |
| webapp-testing | 官方 | 可临时激活 | Web测试、Playwright | Web应用测试 |
| gstack | 社区 | 可临时激活 | 浏览网页、QA测试、截图 | 浏览器自动化 |
| wechat-claude-code | 社区 | 可临时激活 | 微信、微信对话 | 微信↔CC桥接 |
| **观望** |
| n8n-docker-upgrade | 自建 | 观望 | n8n升级、n8n版本 | n8n Docker升级 |
| wan-pptx-generator | 社区 | 观望 | 文档转PPT、AI做PPT | Wan 图片PPT生成（qwen-doc-turbo，需 DashScope API Key） |
| office-hours | 社区 | 观望 | YC、创业辅导 | YC Office Hours |
| obsidian-canvas-creator | 社区 | 观望 | Canvas、思维导图 | Obsidian Canvas创建 |
| web-artifacts-builder | 官方 | 储备 | artifacts、HTML组件 | Claude.ai artifacts |
| doc-coauthoring | 官方 | 储备 | 协作文档、共写 | 文档协作 |
| internal-comms | 官方 | 储备 | 内部沟通、邮件 | 内部通信模板 |
| **已删除** |
| algorithmic-art | 官方 | 已删除 | 算法艺术、p5.js | p5.js算法艺术 |
| brand-guidelines | 官方 | 已删除 | Anthropic品牌 | Anthropic品牌规范 |
| slack-gif-creator | 官方 | 已删除 | Slack GIF | Slack GIF创建 |
| theme-factory | 官方 | 已删除 | 主题样式 | 主题风格应用 |

---

## 八、冲突处理与选择优先级

### 多 Skill 匹配同一需求

当多个 skill 都能处理同一需求时，按以下优先级选择：

| 优先级 | 选择规则 | 示例 |
|--------|----------|------|
| 1 | 指挥官明确指定 | "用 excalidraw 画图" → excalidraw-diagram |
| 2 | 匹配关键词精确度 | "手绘风格图表" → excalidraw-diagram（胜过 mermaid） |
| 3 | 常驻优先于储备 | "测试网页" → gstack（胜过 webapp-testing） |
| 4 | 用户偏好优先 | 用户偏好 Excalidraw → excalidraw-diagram |

### 冲突场景处理

| 场景 | 冲突 Skills | 处理方式 |
|------|------------|----------|
| "画个图表" | excalidraw / mermaid / canvas | 询问指挥官偏好 |
| "做个演示" | frontend-slides / pptx | 根据输出格式判断（HTML vs PPTX） |
| "处理文档" | docx / pdf / xlsx | 根据文件类型判断 |

### 用户偏好映射

根据 MEMORY.md 中的用户偏好：
- **可视化偏好** → Excalidraw（手绘风格）优先
- **输出格式** → 询问指挥官（PDF/HTML/PPTX）

---

## 九、验证与测试流程

### 新 Skill 安装验证

安装完成后，必须验证是否生效：

```bash
# 1. 检查软连接
ls -la ~/.claude/skills/<skill-name>

# 2. 检查源文件
ls ~/Documents/My_Skills_Library/<目录>/<skill-name>/SKILL.md

# 3. 测试调用（在对话中）
"测试一下 <skill-name> 技能"
```

### 验证清单

| 检查项 | 命令 | 预期结果 |
|--------|------|----------|
| 软连接存在 | `ls ~/.claude/skills/<skill>` | 显示链接路径 |
| 源文件存在 | `ls <源目录>/SKILL.md` | 文件存在 |
| Skill 可调用 | 对话中测试 | 能正常触发 |

### 验证失败处理

| 问题 | 解决方案 |
|------|----------|
| 软连接不存在 | 重新创建：`ln -s <源目录> ~/.claude/skills/<skill>` |
| SKILL.md 缺失 | 检查克隆是否完整，重新下载 |
| 无法触发 | 重启 CC 会话，检查 frontmatter 格式 |

---

## 十、批量操作机制

### 批量安装

指挥官说"批量安装这些 skills"时：

```bash
# 批量克隆
for url in "$URL_LIST"; do
  cd ~/Documents/My_Skills_Library/社区第三方/
  git clone "$url"
done

# 批量安全评估
for skill in */; do
  # 执行 P0-P3 评估
  echo "评估 $skill..."
done

# 批量激活（指挥官确认后）
for skill in "$SKILL_LIST"; do
  ln -s ~/Documents/My_Skills_Library/社区第三方/$skill ~/.claude/skills/$skill
done
```

### 批量删除

指挥官说"批量删除这些 skills"时：

```bash
# 1. 删除软连接（保留源文件）
for skill in "$SKILL_LIST"; do
  rm ~/.claude/skills/$skill
done

# 2. 更新变更记录
# 记录到 .skills-changelog.md

# 3. 可选：归档源文件
mv ~/Documents/My_Skills_Library/<目录>/<skill> ~/Documents/My_Skills_Library/归档/
```

### 批量升级

指挥官说"批量升级所有 skills"时：

```bash
# 官方
cd ~/Documents/My_Skills_Library/anthropic_官方 && git pull

# 社区第三方（git 仓库）
for dir in ~/Documents/My_Skills_Library/社区第三方/*/; do
  if [ -d "$dir/.git" ]; then
    cd "$dir" && git pull
  fi
done

# 记录升级日志
```

---

## 十一、与记忆同步规则

### 操作后同步

Skills 管理操作完成后，必须同步更新：

| 操作 | 同步内容 | 目标文件 |
|------|----------|----------|
| 安装新 Skill | 更新常驻列表 | 本 SKILL.md |
| 删除 Skill | 记录删除原因 | .skills-changelog.md |
| 升级 Skill | 记录变更内容 | .upgrade-log.md |
| 批量操作 | 记录操作摘要 | .skills-changelog.md |

### 记忆索引更新

重大变更后，更新 MEMORY.md 的配置索引：

```markdown
| 主题 | 文件 | 说明 |
|------|------|------|
| Skills 管理 | **使用 `/skills-management` 技能** | 安装/评估/升级/激活 |
```

（此条目已存在，无需重复添加）

### 同步时机

| 场景 | 是否同步 |
|------|----------|
| 安装/删除/升级 Skill | ✅ 必须同步 |
| 临时激活（未保留） | ❌ 不同步 |
| 使用频率统计 | ✅ 每季度同步到 changelog |

---

## 十二、完整安装流程

### 安装前门禁（v2.0 新增）

**安装或更新任何 skill 前，必须执行元数据合规检查：**

```bash
bash ~/.claude/skills/skills-management/skills-lint.sh <skill-name>
```

| 结果 | 操作 |
|------|------|
| ✅ PASS | 继续安装 |
| ⚠️ WARN | 可安装，但警告项应尽快修复（如缺少 source_url） |
| ❌ FAIL | **阻断安装**，必须修正后重试。必填字段：name / description / category / metadata.version |

**新 skill 创建规范**：从模板开始：

```bash
cp ~/.claude/skills/SKILL_TEMPLATE.md <new-skill-dir>/SKILL.md
```

**安装完成后**：更新索引文件 `~/.claude/skills/SKILLS_INDEX.md`，追加新 skill 条目。

### 安装流程（四步）

1. **来源评估** → 判断 official / community / self-built，确定放置目录
2. **安全审查** → 按 P0-P3 分级执行
3. **Lint 门禁** → `skills-lint.sh` 检查元数据合规性（v2.0 新增）
4. **激活** → 在 `~/.claude/skills/` 创建符号链接 + 更新 SKILLS_INDEX.md

### 门禁强制执行规则

- 安装时 FAIL → **不创建符号链接，不更新索引**，输出具体缺失项要求修正
- 更新时 FAIL → **不覆盖原 SKILL.md**，保留旧版本继续使用，提示修正
- PASS → 自动执行激活步骤
- WARN → 允许通过，但在 SKILLS_INDEX.md 中标记 `issues` 列

---

## 十三、升级维护

### 按来源升级

| 来源 | 升级命令 | 频率建议 |
|------|----------|----------|
| 官方 | `cd ~/Documents/My_Skills_Library/anthropic_官方 && git pull` | 每月 |
| 社区第三方 | 见下方详细列表 | 按需 |
| 自建 | 手动编辑 | 按需 |

### 社区第三方升级列表

| Skill | 来源 | 升级方式 | 备注 |
|-------|------|----------|------|
| **gstack** | GitHub garrytan/gstack | `git pull` | 大型技能包，browse/design等 |
| **web-access** | GitHub eze-is/web-access | `git pull` | 联网抓取/浏览器交互 |
| **ima-skill** | 手动复制 | 无 | IMA 知识库，无上游 |
| **excalidraw-diagram** | 未知来源 | 手动检查 | 非 git，需找上游更新 |
| **mermaid-visualizer** | 未知来源 | 手动检查 | 非 git，需找上游更新 |
| **obsidian-canvas-creator** | 未知来源 | 手动检查 | 非 git，需找上游更新 |

### 升级流程（必须执行）

指挥官说"升级 skills"时：

1. **检查状态**：
   ```bash
   # 官方
   cd ~/Documents/My_Skills_Library/anthropic_官方 && git fetch && git status

   # 社区第三方（每个 git 仓库）
   for dir in ~/Documents/My_Skills_Library/社区第三方/*/; do
     cd "$dir" && git fetch && git status
   done
   ```

2. **执行升级**：对落后版本执行 `git pull`

3. **记录升级日志**：更新 `.upgrade-log.md`

4. **检查软连接**：如有目录变更，更新 `~/.claude/skills/`

### 升级后操作

1. 检查 CHANGELOG 或 Releases
2. 更新升级日志（记录变更内容）
3. 如有 breaking changes，测试功能
4. 更新激活层软连接（如有变更）

---

## 十四、故障排除

### Skill 不生效

1. 检查软连接是否存在：`ls -la ~/.claude/skills/`
2. 检查源目录 SKILL.md 是否正确
3. 重启 CC 会话

### 升级后出问题

1. 回退版本：`git checkout <commit-hash>`
2. 查看 GitHub Issues
3. 记录问题到升级日志

### 目录混乱

1. 检查是否有 skill 放错目录
2. 移动到正确分类目录
3. 更新软连接

---

## 十五、本技能维护说明

### 迭代原则

| 场景 | 操作 |
|------|------|
| 新增管理流程 | 更新本 SKILL.md |
| 修改评估标准 | 更新本 SKILL.md |
| 调整激活机制 | 更新本 SKILL.md |
| 版本升级 | 更新下方版本记录 |

**记忆文件**：只做索引，不重复写管理逻辑。

### 版本记录

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v3.5 | 2026-06-24 | 常驻列表对齐 13→17：删2幽灵 lark-doc/lark-shared（源已于2026-05-27删除）+ 补6漏登 nuwa/darwin/chen-laoshi-perspective/fu-peng-perspective/commander-perspective/frontend-design + a-stock-data 重建软连接恢复激活；匹配规则表+完整索引同步标注 lark-doc/lark-shared 已删源。触发于 knowledge-engine P1.0 技术债清偿（13/16不一致） |
| v3.4 | 2026-06-13 | 登记表修正：实际 13 个常驻（+飞书×3 +xiaohongshu -guizang -wan2.7 -instinct）；降级 3 个零使用 skill；补 wan-pptx-generator 入观望；更新使用统计 |
| v3.3 | 2026-05-26 | 新增 Plugin 系统边界规则（第十六章），双路径架构说明 |
| v3.2 | 2026-05-14 | 补充 invest skill 到匹配表和常驻列表；常驻自建核心 2→3 |
| v3.1 | 2026-05-03 | 二轮精简：常驻从 17→10 个，删除 canvas-design/frontend-design/webapp-testing/wechat-claude-code |
| v3.0 | 2026-04-18 | 系统性重构：新增完整技能索引(七)、冲突处理(八)、验证流程(九)、批量操作(十)、记忆同步(十一)；完善匹配规则表；修正章节编号 |
| v2.6 | 2026-04-18 | 新增临时激活机制，支持已删除链接技能的自动发现和激活 |
| v2.5 | 2026-04-18 | 新增使用评估与变更记录章节；更新常驻列表（删除4个无用技能） |
| v2.4 | 2026-03-30 | 新迁移3个图表 skills，修正常驻分类，完善升级流程 |
| v2.3 | 2026-03-30 | 分场景处理，通用操作不强制查 skill |
| v2.2 | 2026-03-30 | 标记为常驻 skill，新增强制前置检查规则 |
| v2.1 | 2026-03-30 | 新增智能激活机制，指挥官无需手动指定 |
| v2.0 | 2026-03-30 | 重构版本，目录隔离架构 |
| v1.0 | 2026-02-16 | 初始版本 |

---

## 十六、Plugin 系统边界

### 两条路径的分工

| 维度 | 路径 A：Skills 管理 | 路径 B：Plugin 系统 |
|------|---------------------|---------------------|
| **适用场景** | 自建 skill、社区第三方、需要定制 | 官方插件、预制组合包 |
| **安装命令** | `git clone` + `ln -s` | `claude plugin install` 或 `/plugin install` |
| **版本管理** | 手动 git pull + changelog | 插件系统自动管理 |
| **安全审查** | P0-P3 分级评估 | 官方源默认信任 |
| **激活方式** | `~/.claude/skills/` 软链接 | `settings.json` → `enabledPlugins` |

### 边界规则

1. **Anthropic 官方插件**（`@claude-plugins-official`）→ 路径 B，事后记录即可，无需事前审核
2. **第三方市场插件**（`@superpowers-marketplace` 等）→ 仍需安全评估（P0-P3），评估通过后可用路径 B 安装
3. **自建/社区 skill** → 路径 A，保持现有流程不变
4. **插件内含多个组件**（skill + hook + agent 组合包）→ 必须安全评估，不论来源

### 事后记录要求

通过路径 B 安装官方插件后，记录到 `.skills-changelog.md`：

```markdown
## 2026-05-26 Plugin 安装
- **新增**：claude-code-setup@claude-plugins-official (v1.0.0)
- **来源**：Anthropic 官方插件市场
- **内容**：claude-automation-recommender skill（只读分析）
- **评估**：P1-受限，官方信任，免审
```

### 冲突检测

两条路径可能安装同名 skill。冲突时：
- 路径 A（手动软链接）优先于路径 B（plugin 系统）
- 检测到冲突时通知指挥官决定保留哪个

---

## 参考文件

- `references/audit-checklist.md` - 安全评估检查清单
- `references/SKILL-TEMPLATE.md` - 新 Skill 模板
- `.skills-changelog.md` - Skills 变更记录（增删改历史）