# Learnings Log

Captured learnings, corrections, and discoveries. Review before major tasks.

---

## [LRN-20260218-001] best_practice

**Logged**: 2026-02-18T00:30:00+08:00
**Priority**: high
**Status**: resolved

### Summary
各家 AI 服务商的 API 兼容性差异大，配置前必须先验证端点是否存在。

### Details
Moonshot/Kimi 的 API 只提供 OpenAI 兼容格式 (`/v1/chat/completions`)，不提供 Anthropic 兼容端点。`api.moonshot.cn/anthropic` 返回 404。而阿里云 DashScope 提供 Anthropic 兼容端点 (`/apps/anthropic`)，且上面有 Kimi 模型可用 (`kimi-k2.5`, `kimi-k2-thinking`)。

Claude Code 只支持 Anthropic Messages API 格式，所以没有 Anthropic 兼容端点的服务商无法直接接入 Claude Code。

### Suggested Action
配置新服务商前，先用 `curl -s -o /dev/null -w "%{http_code}" "https://api.xxx.com/anthropic"` 测试端点是否存在。对于无 Anthropic 兼容端点的服务商，检查阿里云 DashScope 是否有对应模型可用。

### Metadata
- Source: error
- Related Files: `~/.claude/skills/antigravity-model-sync/SKILL.md`
- Tags: api-compatibility, claude-code, kimi, dashscope
- Promoted: antigravity-model-sync SKILL.md (坑1)

---

## [LRN-20260218-002] correction

**Logged**: 2026-02-18T00:35:00+08:00
**Priority**: high
**Status**: resolved

### Summary
OpenCode `@ai-sdk/openai-compatible` 认证必须用 `options.apiKey`，不支持 `headers.Authorization`。

### Details
在 OpenCode 的 `opencode.json` 中配置自定义 provider 时，用 `"headers": {"Authorization": "Bearer sk-xxx"}` 传递 API Key 无效，请求不会携带认证信息。正确方式是使用 `"apiKey": "sk-xxx"` 字段。

同时，如果自定义 provider 的模型 ID 与 OpenCode 内置模型相同，会优先匹配内置模型（使用免费额度），而非自定义 provider 的 API。解决方法是确保自定义 provider 名称清晰区分。

### Suggested Action
配置 `@ai-sdk/openai-compatible` provider 时，始终用 `options.apiKey` 字段传递 API Key。Provider name 加上"(自有API)"等后缀避免与内置模型混淆。

### Metadata
- Source: user_feedback
- Related Files: `~/.config/opencode/opencode.json`
- Tags: opencode, authentication, ai-sdk
- Promoted: antigravity-model-sync SKILL.md (坑2)

---

## [LRN-20260218-003] knowledge_gap

**Logged**: 2026-02-18T00:40:00+08:00
**Priority**: high
**Status**: resolved

### Summary
`@ai-sdk/google` 只支持 Gemini 模型，无法调用 Antigravity 反代提供的 Claude 模型。

### Details
Antigravity 同时提供 Claude 和 Gemini 模型，但底层走不同的 API 协议。`@ai-sdk/google` 调用 Google Generative AI API（只支持 Gemini）。Claude 模型通过 Google Cloud Code API 提供，协议不同。

在 OpenCode 中，必须将两类模型拆分为不同的 provider:
- Gemini → `@ai-sdk/google`（直连 Google API）
- Claude → `@ai-sdk/anthropic`（走本地反代 localhost:8317/v1）

### Suggested Action
配置 Antigravity 模型到 OpenCode 时，始终将 Claude 和 Gemini 分开配置。不要把 Claude 模型放在 `@ai-sdk/google` provider 下。

### Metadata
- Source: error
- Related Files: `~/.config/opencode/opencode.json`
- Tags: antigravity, opencode, ai-sdk-google, ai-sdk-anthropic
- See Also: LRN-20260218-004
- Promoted: antigravity-model-sync SKILL.md (坑3)

---

## [LRN-20260218-004] best_practice

**Logged**: 2026-02-18T00:45:00+08:00
**Priority**: high
**Status**: resolved

### Summary
`@ai-sdk/anthropic` 的 `baseURL` 必须包含 `/v1` 后缀，否则 endpoint 404。

### Details
`@ai-sdk/anthropic` SDK 在 baseURL 后直接拼接 `/messages` 发起请求。Antigravity 反代的实际端点是 `/v1/messages`。

如果 baseURL 设为 `http://localhost:8317`，SDK 请求 `/messages` → 404。
必须设为 `http://localhost:8317/v1`，SDK 请求 `/v1/messages` → 正确。

报错信息: `Endpoint POST /messages not found`

### Suggested Action
配置 `@ai-sdk/anthropic` 的 baseURL 时，始终确认目标 proxy 的 messages 端点路径，然后反推出正确的 baseURL。验证方法:
```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://host:port/messages
curl -s -o /dev/null -w "%{http_code}" -X POST http://host:port/v1/messages
```
哪个返回 400（而非 404），就说明该路径是正确的。

### Metadata
- Source: error
- Related Files: `~/.config/opencode/opencode.json`
- Tags: ai-sdk-anthropic, baseurl, antigravity-proxy
- See Also: LRN-20260218-003
- Promoted: antigravity-model-sync SKILL.md (坑4)

---
