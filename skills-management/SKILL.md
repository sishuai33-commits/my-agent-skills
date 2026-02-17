---
name: skills-management
description: "完整的 Skills 全周期管理体系。用于管理 AI 工具的 Skills 扩展：Anthropic 官方更新、ClawHub 社区审查、自建 Skills 维护。包含自动化检查、安全审查、权限分级、同步部署等完整流程。"
license: MIT License - 详见 LICENSE.txt
---

# Skills 管理体系

完整的 AI Agent Skills 全生命周期管理解决方案，确保 Skills 来源可信、安全可控、版本可追溯。

## 核心能力

- **多源管理**：整合 Anthropic 官方、ClawHub 社区、自建 Skills
- **安全审查**：自动检测高危代码模式，P0-P3 权限分级
- **版本控制**：Git 追踪所有变更，审查历史可审计
- **自动同步**：一键部署到 OpenCode、Claude Code、Antigravity
- **定时检查**：自动检测更新和新加入的 Skills

## 适用场景

使用此 Skill 当用户需要：
- 更新 Anthropic 官方 Skills
- 审查和批准新的 ClawHub Skills
- 同步 Skills 到多个 AI 工具
- 管理自建 Skills
- 配置自动化检查任务
- 了解 Skills 安全审查标准

## 快速开始

### 1. 目录结构

```
My_Skills_Library/
├── .config/                          # 配置文件（隐藏）
│   ├── CLAUDE.md                    # 完整操作手册（本文档）
│   ├── skills-sync.json             # Git 仓库配置
│   ├── clawhub-permissions.json     # 权限分级规则
│   └── Dockerfile.skill-sandbox     # Docker 沙箱镜像
│
├── .scripts/                         # 管理脚本（隐藏）
│   ├── skills-sync.sh               # 检查官方更新（每周自动）
│   ├── clawhub-fetch.sh             # ClawHub 管理
│   ├── security-audit.sh            # 安全审查
│   ├── sync-to-global.sh            # 同步到全局
│   └── auto-check-clawhub.sh        # 自动检测新 Skills
│
├── anthropic_官方/                   # Anthropic 官方仓库
│   └── skills/                      # 官方 Skills（最高可信）
│
├── clawhub_skills/                   # ClawHub 管理
│   ├── clawhub-pending/             # 待审查队列
│   └── clawhub-approved/            # 已批准（Git 追踪）
│
└── 技能库_自建/                      # 自建 Skills
    └── skills-management/           # 本 Skill
```

### 2. 核心命令

```bash
# 查看待审查列表
~/.scripts/clawhub-fetch.sh list

# 执行安全审查
~/.scripts/security-audit.sh --sandbox <skill-path>

# 批准 Skill
~/.scripts/clawhub-fetch.sh approve <skill-name>

# 同步到所有工具
~/.scripts/sync-to-global.sh --include-clawhub
```

## 详细流程

### 流程一：Anthropic 官方更新

**自动检查（每周一 9:00）**
```bash
~/.scripts/skills-sync.sh
```

**查看报告**
```bash
cat ~/.config/update-report.md
```

**更新并同步**
```bash
cd ~/Documents/My_Skills_Library/anthropic_官方
git pull origin main
~/.scripts/sync-to-global.sh
```

### 流程二：ClawHub 审查流程

**Step 1: 下载到待审查队列**
```bash
# 方式 A：用户下载后告知
~/.scripts/clawhub-fetch.sh install <skill-name>

# 方式 B：检测到新文件（自动，每 10 分钟）
# 系统会自动提醒
```

**Step 2: 自动安全检查**
```bash
~/.scripts/security-audit.sh --sandbox \
  ~/Documents/My_Skills_Library/clawhub_skills/clawhub-pending/<skill-name>/
```

检查内容：
- ❌ 高危模式：`curl|bash`、`eval`、`base64 --decode`
- ⚠️ 敏感路径：`~/.ssh`、`~/.aws`、`~/.config`
- ⚠️ 网络请求：API 调用、外部下载

**Step 3: 查看报告**
```bash
cat ~/.config/audit-report-<skill-name>.md
```

报告包含：权限分级、危险模式统计、文件结构、建议操作。

**Step 4: 批准或拒绝**

批准：
```bash
~/.scripts/clawhub-fetch.sh approve <skill-name>
```

拒绝：
```bash
~/.scripts/clawhub-fetch.sh reject <skill-name>
```

**Step 5: 同步到全局**
```bash
~/.scripts/sync-to-global.sh --include-clawhub
```

### 流程三：自建 Skills 管理

**创建新 Skill**
```bash
mkdir -p ~/Documents/My_Skills_Library/技能库_自建/<skill-name>
# 编写 SKILL.md 和相关文件
```

**测试验证**
```bash
~/.scripts/security-audit.sh \
  ~/Documents/My_Skills_Library/技能库_自建/<skill-name>/
```

**同步到全局**
```bash
~/.scripts/sync-to-global.sh
```

## 权限分级标准（P0-P3）

| 等级 | 描述 | 自动通过 | 沙箱测试 | 关键特征 |
|------|------|----------|----------|----------|
| **P0-安全** | 纯文本处理 | ✅ | ❌ | 无外部依赖，本地计算 |
| **P1-受限** | 只读访问 | ✅ | ❌ | HTTP GET、Git 读取、环境变量读取 |
| **P2-敏感** | 写入/受限执行 | ❌ | ✅ | 文件写入、网络 POST、受限命令执行 |
| **P3-高危** | 系统级操作 | ❌ | ✅ | 全局安装、任意命令、敏感目录访问 |

### 危险信号（立即拒绝）

- `curl | bash` 或 `wget -O- | sh`
- `eval`、`exec` 动态执行
- `base64 --decode` 后执行
- 要求 `sudo` 权限
- 访问 `~/.ssh`、`~/.aws`、`~/.config`
- 修改 `/etc/` 或 shell 配置文件
- 请求密码、API 密钥输入
- 加密货币钱包路径访问

## 自动化任务

### 定时任务配置

**查看当前任务**
```bash
crontab -l
```

**任务列表**

1. **官方更新检查**：每周一 9:00
   ```
   0 9 * * 1 ~/.scripts/skills-sync.sh
   ```

2. **新技能检测**：每 10 分钟
   ```
   */10 * * * * ~/.scripts/auto-check-clawhub.sh
   ```

### 手动触发检查

```bash
# 检查官方更新
~/.scripts/skills-sync.sh

# 检查 ClawHub 新技能
~/.scripts/auto-check-clawhub.sh

# 查看检测日志
tail -f ~/.config/.auto-check.log
```

## 故障排除

### 同步失败

```bash
# 检查目标目录
ls -la ~/.config/opencode/skills/
ls -la ~/.claude/skills/
ls -la ~/.gemini/antigravity/skills/

# 手动创建缺失目录
mkdir -p ~/.claude/skills ~/.gemini/antigravity/skills
```

### Docker 沙箱构建失败

```bash
# 手动构建沙箱镜像
cd ~/.config
docker build -t skill-sandbox -f Dockerfile.skill-sandbox .
```

### 脚本权限问题

```bash
chmod +x ~/.scripts/*.sh
```

### Git 配置

```bash
# 配置 git 身份（用于审查记录）
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## 最佳实践

### 审查原则

1. **绝不跳过审查**：即使是 popular 的 skill
2. **阅读 SKILL.md**：完整理解功能意图
3. **查看源代码**：不只是描述文件
4. **沙箱测试**：P2/P3 级别必须隔离测试
5. **最小权限**：批准时明确权限范围

### 更新策略

- **每周一**：检查官方更新（自动）
- **每月**：审查已批准 skills 是否有新版本
- **每季度**：清理不再使用的 skills
- **立即**：发现安全漏洞时紧急更新

### 备份建议

```bash
# 备份整个技能库
cd ~/Documents/My_Skills_Library
git init
git add .
git commit -m "备份 $(date '+%Y-%m-%d')"

# 定期推送到远程（可选）
# git remote add origin <your-repo>
# git push
```

## 模板和示例

### SKILL.md 模板

见 `templates/SKILL-TEMPLATE.md`

### 审查报告示例

见 `references/audit-report-example.md`

### 权限配置示例

见 `.config/clawhub-permissions.json`

## 扩展和定制

### 添加新的 AI 工具

编辑 `~/.scripts/sync-to-global.sh`，在 `TARGETS` 数组中添加：

```bash
declare -A TARGETS=(
    ["OpenCode"]="$HOME/.config/opencode/skills"
    ["Claude Code"]="$HOME/.claude/skills"
    ["Antigravity"]="$HOME/.gemini/antigravity/skills"
    ["YourTool"]="$HOME/.yourtool/skills"  # 新增
)
```

### 自定义危险模式

编辑 `~/.config/clawhub-permissions.json`，在 `dangerous_patterns` 中添加：

```json
{
  "dangerous_patterns": {
    "critical": [
      "your-pattern-here"
    ]
  }
}
```

### 修改检查频率

```bash
# 编辑 crontab
crontab -e

# 修改时间表达式
# 例如：改为每 30 分钟检查一次
*/30 * * * * ~/.scripts/auto-check-clawhub.sh
```

## 版本历史

- **v1.0** (2026-02-16): 初始版本，完整实现管理体系
  - Anthropic 官方更新机制
  - ClawHub 审查流程（P0-P3 权限分级）
  - Docker 沙箱测试
  - 自动化定时任务
  - 多工具同步部署

## 参考文档

- `.config/CLAUDE.md` - 完整操作手册
- `.config/clawhub-permissions.json` - 权限规则
- `templates/SKILL-TEMPLATE.md` - Skill 模板
- `references/` - 示例和参考

---

**维护提示**：本 Skill 本身也需要定期更新，建议每季度检查是否有改进空间。

## Interactive AI Capabilities (Evolution Engine)

### Capability: Hot-Fix (Patch Mode)
When the user wants to fix a specific behavior of a skill immediately:
1.  **Locate**: Read the target skill file (usually `SKILL.md`).
2.  **Diagnose**: Identify the *specific section* or *instruction* causing the issue based on the user's complaint or the error context.
3.  **Patch**:
    - Do NOT rewrite the entire file unless necessary.
    - Edit ONLY the offending rule or add a new constraint to the "Rules" section.
    - *Crucial*: Add a comment `<!-- Patched: [Reason] [Date] -->` near the change.
4.  **Verify**: Ask the user if they want to retry the last failed action with the new prompt.

### Capability: Smart Update (Rebase Strategy)
When updating a skill from an official source while preserving local customizations:
1.  **Download** official version to a temporary location.
2.  **Read** local version.
3.  **Extract** all blocks marked with `<!-- [USER-EVOLUTION] ... -->`.
4.  **Inject** these blocks into the new official version at appropriate locations (e.g., end of `## Rules`).
5.  **Save** the merged file.
