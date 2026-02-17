# Antigravity Model Sync

## 作用
将 Antigravity 反代中的模型同步配置到 OpenCode 和 Claude Code

## 什么时候用？
- Antigravity 推出了新模型（如 Opus 4.6、4.7）
- 需要在 OpenCode 中使用新模型
- 需要在 Claude Code 中使用新模型

## 同步流程（当有新模型时）

### 1. 检查反代中的模型
```bash
curl -s http://localhost:8317/health | grep -o 'claude-opus-4-[0-9]-thinking'
```

### 2. 更新 OpenCode 配置
编辑 `~/.config/opencode/opencode.json`：
```json
"google": {
  "models": {
    "claude-opus-4-6-thinking": {
      "name": "Claude Opus 4.6 Thinking",
      "limit": {"context": 200000, "output": 8192}
    }
  }
}
```

### 3. 更新 Claude Code 脚本
编辑 `cc-antigravity.sh`，在 case 语句中添加：
```bash
opus46|o46|4.6)
    MODEL_NAME="claude-opus-4-6-thinking"
    MODEL_DESC="Claude Opus 4.6 Thinking (最新最强)"
    ;;
```

### 4. 更新 .zshrc
在 `ccmodels()` 函数中添加：
```bash
echo "  ccag opus46    - claude-opus-4-6-thinking (最新最强)"
```

### 5. 更新文档
- README.md
- CLAUDE_MODELS_GUIDE.md
- CLAUDE_CODE_QUICK_START.md

### 6. 验证并重启
```bash
python3 -m json.tool ~/.config/opencode/opencode.json > /dev/null
echo "✅ 配置格式正确"
pkill -9 "OpenCode" && open -a "OpenCode"
```

## 当前支持的模型

### Claude 模型
| 命令 | 模型 ID | 说明 |
|------|---------|------|
| `ccag sonnet` | claude-sonnet-4-5 | 平衡型 |
| `ccag opus45` | claude-opus-4-5-thinking | 最强推理 4.5 |
| `ccag opus46` | claude-opus-4-6-thinking | 最新最强 4.6 |

### Gemini 模型
| 命令 | 模型 ID | 说明 |
|------|---------|------|
| `ccag 3-pro` | gemini-3-pro-high | Google 最强 |
| `ccag 2.5-flash` | gemini-2.5-flash | 快速便宜 |

## 配置文件清单

| 文件 | 路径 | 用途 |
|------|------|------|
| OpenCode 配置 | `~/.config/opencode/opencode.json` | OpenCode GUI 的模型列表 |
| Claude Code 脚本 | `~/Documents/My_Code_Projects/AI-Tools（模型切换）/Claude-Code/scripts/cc-antigravity.sh` | 切换命令 |
| Shell 配置 | `~/.zshrc` | 快捷命令和帮助 |
| 说明文档 | `README.md` | 目录结构说明 |
| 模型指南 | `CLAUDE_MODELS_GUIDE.md` | 详细使用指南 |
| 快速开始 | `CLAUDE_CODE_QUICK_START.md` | 快速配置指南 |
