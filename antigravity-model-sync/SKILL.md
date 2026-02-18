---
name: antigravity-model-sync
description: "将 Antigravity 反代中的模型同步配置到 OpenCode 和 Claude Code。当用户提到同步 Antigravity 模型、添加新模型到 OpenCode/Claude Code、更新 Antigravity 配置、或发现反代中有新模型时使用此 skill。"
---

# Antigravity Model Sync

将 Antigravity 反代中的模型同步配置到 OpenCode 和 Claude Code。

## 触发条件

当用户提到以下内容时使用此 skill：
- 同步 antigravity 模型
- 添加 antigravity 模型到 opencode
- 添加 antigravity 模型到 claude code
- 更新 antigravity 配置
- antigravity 新模型
- 发现反代中有新模型

## 同步工作流

### Step 1: 检查反代中可用的模型

```bash
curl -s http://localhost:8317/health | grep -o 'claude-opus-4-[0-9]-thinking\|gemini-[0-9]-[a-z-]*' | sort -u
```

### Step 2: 更新 OpenCode 配置

编辑 `~/.config/opencode/opencode.json`：
- **Gemini 模型**: 在 `provider.google.models` 中添加（使用 `@ai-sdk/google`）
- **Claude 模型**: 在 `provider.antigravity_claude.models` 中添加（使用 `@ai-sdk/anthropic`，走反代 localhost:8317）

> 注意: `@ai-sdk/google` 只支持 Gemini 模型，Claude 模型必须通过反代的 Anthropic API 格式调用。

### Step 3: 更新 Claude Code 切换脚本

编辑 `~/Documents/My_Code_Projects/AI-Tools（模型切换）/Claude-Code/scripts/cc-antigravity.sh`，在 case 语句中添加新模型选项：

```bash
modelshort|short|version)
    MODEL_NAME="model-id"
    MODEL_DESC="Model Description"
    ;;
```

### Step 4: 更新 .zshrc

编辑 `~/.zshrc`，在 `ccmodels` 函数中添加新模型说明。

### Step 5: 更新相关文档

需要更新的文档列表：
- `~/Documents/My_Code_Projects/AI-Tools（模型切换）/Claude-Code/README.md`
- `~/Documents/My_Code_Projects/AI-Tools（模型切换）/Claude-Code/docs/CLAUDE_MODELS_GUIDE.md`
- `~/Documents/My_Code_Projects/AI-Tools（模型切换）/Claude-Code/docs/CLAUDE_CODE_QUICK_START.md`

### Step 6: 验证配置

```bash
python3 -m json.tool ~/.config/opencode/opencode.json > /dev/null && echo '✅ OpenCode 配置格式正确'
```

### Step 7: 重启 OpenCode

```bash
pkill -9 'OpenCode' && sleep 2 && open -a 'OpenCode'
```

## 当前支持的模型

### Claude 模型 (Antigravity 反代)

| 快捷命令 | 模型 ID | 说明 |
|----------|---------|------|
| `ccag sonnet` | claude-sonnet-4-5 | 平衡型 |
| `ccag opus` | claude-opus-4-6-thinking | 最新最强 4.6 |

### Gemini 模型 (Antigravity 反代)

| 快捷命令 | 模型 ID | 说明 |
|----------|---------|------|
| `ccag 3-pro` | gemini-3-pro-high | Google 最强 |
| `ccag 2.5-flash` | gemini-2.5-flash | 快速便宜 |

### Kimi 模型 (阿里云 DashScope 通道)

| 快捷命令 | 模型 ID | 说明 |
|----------|---------|------|
| `cckimi k2.5` | kimi-k2.5 | K2.5 多模态(推荐) |
| `cckimi thinking` | kimi-k2-thinking | 思考模式 |

> **注意**: Moonshot 无 Anthropic 兼容端点，Claude Code 中通过阿里云 DashScope 调用。
> OpenCode 可直接使用 Moonshot 自有 API（provider: `my_moonshot`）。

## 配置文件清单

| 文件 | 路径 | 用途 |
|------|------|------|
| OpenCode 配置 | `~/.config/opencode/opencode.json` | OpenCode GUI 的模型列表 |
| Antigravity 脚本 | `~/Documents/My_Code_Projects/AI-Tools（模型切换）/Claude-Code/scripts/cc-antigravity.sh` | Antigravity 模型切换 |
| Kimi 脚本 | `~/Documents/My_Code_Projects/AI-Tools（模型切换）/Claude-Code/scripts/cc-kimi.sh` | Kimi 模型切换(阿里云通道) |
| Qwen 脚本 | `~/Documents/My_Code_Projects/AI-Tools（模型切换）/Claude-Code/scripts/cc-qwen.sh` | Qwen 模型切换 |
| DeepSeek 脚本 | `~/Documents/My_Code_Projects/AI-Tools（模型切换）/Claude-Code/scripts/cc-ds.sh` | DeepSeek 模型切换 |
| MiniMax 脚本 | `~/Documents/My_Code_Projects/AI-Tools（模型切换）/Claude-Code/scripts/cc-minimax.sh` | MiniMax 模型切换 |
| Shell 配置 | `~/.zshrc` | 快捷命令和帮助 |
| 模型指南 | `CLAUDE_MODELS_GUIDE.md` | 详细使用指南 |
| 快速开始 | `CLAUDE_CODE_QUICK_START.md` | 快速配置指南 |
| 安装指南 | `CLADE_CODE_SETUP.md` | 安装配置指南 |

## 服务商 API 兼容性说明

| 服务商 | Anthropic 兼容端点 | Claude Code 可用 | OpenCode 可用 |
|--------|-------------------|-----------------|---------------|
| Antigravity | localhost:8317 (本地反代) | 可用 | 可用 |
| 阿里云 DashScope | /apps/anthropic | 可用 | 可用 |
| DeepSeek | /anthropic | 可用 | 可用 |
| Kimi/Moonshot | 无 | 需通过阿里云通道 | 直接可用(OpenAI兼容) |
| MiniMax | 无 | 需通过阿里云通道 | 直接可用(OpenAI兼容) |

## 添加新模型示例

场景：发现反代中有新模型 `claude-opus-4-7-thinking`

1. 检查反代确认模型存在
2. 编辑 `opencode.json` 添加模型定义
3. 编辑 `cc-antigravity.sh` 添加 case 选项
4. 编辑 `.zshrc` 更新 ccmodels
5. 更新所有文档
6. 验证 JSON 格式
7. 重启 OpenCode

## 常见踩坑与排错 (2026-02-18 总结)

### 坑1: 服务商没有 Anthropic 兼容端点

**现象**: Claude Code 切换脚本中 `ANTHROPIC_BASE_URL` 指向的端点返回 404。

**排查方法**:
```bash
# 先测试端点是否存在（200/400/401=存在，404=不存在）
curl -s -o /dev/null -w "%{http_code}" "https://api.xxx.com/anthropic"
```

**已知各服务商 Anthropic 兼容性**:

| 服务商 | 端点路径 | 状态 |
|--------|---------|------|
| 阿里云 DashScope | `/apps/anthropic` | 可用 |
| DeepSeek | `/anthropic` | 可用 |
| Moonshot/Kimi | `/anthropic` | **不存在(404)** |
| MiniMax | 无 | **不存在** |

**解决**: 没有 Anthropic 端点的服务商，Claude Code 中通过阿里云 DashScope 中转调用（如 kimi-k2.5 在 DashScope 上可用）。OpenCode 中可直接用 `@ai-sdk/openai-compatible` 调用其 OpenAI 兼容 API。

---

### 坑2: OpenCode 自定义 Provider 认证方式错误

**现象**: 配置了 `headers.Authorization: "Bearer sk-xxx"` 但请求未携带认证。

**原因**: `@ai-sdk/openai-compatible` 不支持通过 `headers` 传认证，必须用 `apiKey` 字段。

**错误写法**:
```json
"options": {
  "baseURL": "https://api.moonshot.cn/v1",
  "headers": { "Authorization": "Bearer sk-xxx" }
}
```

**正确写法**:
```json
"options": {
  "baseURL": "https://api.moonshot.cn/v1",
  "apiKey": "sk-xxx"
}
```

---

### 坑3: `@ai-sdk/google` 不能调用 Claude 模型

**现象**: OpenCode 中 Gemini 模型正常，Claude 模型报错。

**原因**: `@ai-sdk/google` 只会调用 Google Generative AI API，该 API 只支持 Gemini。Claude 模型虽然在 Antigravity 体系中通过 Google Cloud Code API 提供，但这是完全不同的 API 协议。

**解决**: OpenCode 中 Claude 和 Gemini 必须拆成两个 provider：
- **Gemini** → `provider: google`，`npm: @ai-sdk/google`（直接走 Google API）
- **Claude** → `provider: antigravity_claude`，`npm: @ai-sdk/anthropic`（走本地反代 localhost:8317）

---

### 坑4: `@ai-sdk/anthropic` 的 baseURL 需要包含 `/v1`

**现象**: 报错 `Endpoint POST /messages not found`。

**原因**: `@ai-sdk/anthropic` 会在 baseURL 后拼接 `/messages`。反代的实际端点是 `/v1/messages`。

| baseURL 设置 | SDK 实际请求 | 结果 |
|-------------|-------------|------|
| `http://localhost:8317` | `/messages` | 404 |
| `http://localhost:8317/v1` | `/v1/messages` | 正确 |

**验证方法**:
```bash
# 测试反代端点结构
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8317/messages    # 应该 404
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8317/v1/messages  # 应该 400
```

