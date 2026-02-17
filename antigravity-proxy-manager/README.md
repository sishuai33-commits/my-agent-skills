# Antigravity Proxy Manager

## 作用
管理 Antigravity 本地反代服务（启动、停止、查看状态）

## 什么时候用？
- 第一次配置 Antigravity
- 反代服务崩溃或需要重启
- 查看反代运行状态和可用模型

## 命令

### 启动反代
```bash
PORT=8317 nohup npx antigravity-claude-proxy@latest start --strategy=sticky > ~/.antigravity-proxy.log 2>&1 &
```

### 停止反代
```bash
pkill -f antigravity-claude-proxy
```

### 查看状态
```bash
curl -s http://localhost:8317/health
```

### 查看可用模型
```bash
curl -s http://localhost:8317/health | grep -o '"models":{[^}]*}'
```

## 反代的作用
- 将 Antigravity 的 Claude/Gemini 模型暴露为 Anthropic API 格式
- 让 Claude Code 可以通过 `ANTHROPIC_BASE_URL=http://localhost:8317` 连接
- 提供速率限制保护（sticky 策略）

## 配置
- 端口: 8317
- 策略: sticky（固定账号直到限速）
- 日志: ~/.antigravity-proxy.log
