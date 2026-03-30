---
name: skills-management
description: "Skills 全周期管理体系。新 Skills 安装评估、安全审查、版本管理、激活/禁用流程。指挥官说'安装新 skill'、'评估 skill'、'升级 skills'时触发。"
license: MIT License
---

# Skills 管理体系

Skills 全生命周期管理：来源评估 → 安全审查 → 版本记录 → 激活使用 → 升级维护。

---

## 一、目录架构

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

| 指挥官说 | 匹配 skill |
|----------|------------|
| "n8n 升级"、"n8n 版本" | n8n-docker-upgrade |
| "萃取方法论"、"模拟专家思维" | mind-distillation |
| "报销"、"佰钧成"、"BTA" | bjc-reimbursement |
| "浏览网页"、"QA 测试" | gstack/browse |
| "联网"、"抓取网页" | web-access |

**指挥官也可以明确说**："用 xxx skill"

### 常驻 Skills

以下 Skills 永久保留软连接：

**官方 17 个**：
- pdf, docx, pptx, xlsx
- algorithmic-art, canvas-design, frontend-design, web-artifacts-builder
- claude-api, mcp-builder, skill-creator
- brand-guidelines, internal-comms, theme-factory
- doc-coauthoring, slack-gif-creator, webapp-testing

**社区第三方 3 个**（图表可视化）：
- excalidraw-diagram（手绘风格图表）
- mermaid-visualizer（流程图/架构图）
- obsidian-canvas-creator（Obsidian Canvas）

**自建 2 个**：
- skills-management（管理体系核心）
- n8n-docker-upgrade（n8n 升级）

### 临时 Skills

- 按需激活，用完自动删除
- 指挥官**不需要**记住有哪些 skills
- 指挥官**不需要**手动说"激活/禁用"

---

## 六、完整安装流程

### 新 Skill 安装（社区第三方）

指挥官说"安装 xxx skill"时：

1. **来源确认**：询问 GitHub URL 或来源
2. **克隆到目录**：
   ```bash
   cd ~/Documents/My_Skills_Library/社区第三方/
   git clone <url> <skill-name>
   ```
3. **安全评估**：执行 P0-P3 分级检查
4. **评估报告**：输出权限等级和建议
5. **指挥官确认**：是否批准安装
6. **激活（可选）**：创建软连接到全局目录

### 自建 Skill 创建

1. **创建目录**：
   ```bash
   mkdir -p ~/Documents/My_Skills_Library/技能库_自建/<skill-name>
   ```
2. **编写 SKILL.md**：使用模板 `templates/SKILL-TEMPLATE.md`
3. **自行审查**：确认无危险模式
4. **记录版本**：在 SKILL.md 中添加版本记录
5. **激活使用**：创建软连接

---

## 七、升级维护

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
| **web-access** | GitHub | `git pull` | 联网抓取 |
| **excalidraw-diagram** | 未知来源 | 手动检查 | 非 git，需找上游更新 |
| **mermaid-visualizer** | 未知来源 | 手动检查 | 非 git，需找上游更新 |
| **obsidian-canvas-creator** | 未知来源 | 手动检查 | 非 git，需找上游更新 |
| **ima-skill** | 手动复制 | 无 | IMA 知识库，无上游 |

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

## 八、故障排除

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

## 九、本技能维护说明

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
| v2.4 | 2026-03-30 | 新迁移3个图表 skills，修正常驻分类，完善升级流程 |
| v2.3 | 2026-03-30 | 分场景处理，通用操作不强制查 skill |
| v2.2 | 2026-03-30 | 标记为常驻 skill，新增强制前置检查规则 |
| v2.1 | 2026-03-30 | 新增智能激活机制，指挥官无需手动指定 |
| v2.0 | 2026-03-30 | 重构版本，目录隔离架构 |
| v1.0 | 2026-02-16 | 初始版本 |

---

## 参考文件

- `references/audit-checklist.md` - 安全评估检查清单
- `references/SKILL-TEMPLATE.md` - 新 Skill 模板