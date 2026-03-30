---
name: n8n-docker-upgrade
description: 一键升级 Docker 版 n8n 到最新版本。当用户需要升级 n8n、查看版本信息或执行 Docker 容器更新时使用此技能。
---

# n8n Docker 升级技能

本技能用于安全升级 Docker 版 n8n 到最新版本。升级逻辑是"换新容器，挂旧数据"，数据永久保存在 Mac 本地文件夹 `~/.n8n` 中，因此升级不会丢失数据。

## 快速参考

| 场景 | 操作 |
|------|------|
| 升级 n8n 到最新版 | 执行 4 步升级命令 |
| 查看当前版本 | `docker ps --filter name=n8n` |
| 检查升级后状态 | 访问 http://localhost:5678/healthz |

## 升级步骤

按顺序执行以下 4 条命令：

### 1. 下载最新镜像

```bash
docker pull n8nio/n8n:latest
```

> **注意**: 如果下载速度慢，可能需要开启 VPN 或代理。

### 2. 停止当前容器

```bash
docker stop n8n
```

### 3. 删除旧容器

```bash
docker rm n8n
```

> **数据安全**: 数据已挂载到本地 `~/.n8n` 目录，删除容器不会丢失数据。

### 4. 运行新版本容器

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e N8N_SECURE_COOKIE=false \
  --restart unless-stopped \
  n8nio/n8n:latest
```

## 验证升级

执行以下命令确认升级成功：

```bash
# 检查容器状态
docker ps --filter "name=n8n" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

# 检查健康状态
curl -s http://localhost:5678/healthz
```

预期输出：
- 容器状态显示 `Up`
- 健康检查返回 `{"status":"ok"}`

## 常见问题排查

### 端口冲突

如果遇到端口冲突错误：

```bash
# 清理占用 5678 端口的容器
docker stop n8n && docker rm n8n
```

### 网络问题

如果 `docker pull` 卡顿或失败：

1. 检查网络连接
2. 开启代理后重试
3. 或手动设置 Docker 代理：
   ```bash
   export HTTP_PROXY=http://your-proxy:port
   export HTTPS_PROXY=http://your-proxy:port
   ```

### 数据持久化确认

确认数据卷正确挂载：

```bash
ls -la ~/.n8n
```

应该看到 `database.sqlite`、`workflows` 等文件和目录。

## 升级前检查清单

- [ ] 确认 n8n 当前正在运行：`docker ps | grep n8n`
- [ ] 确认没有重要工作流正在执行中
- [ ] 了解数据卷位置：`~/.n8n`
- [ ] 如有需要，可先导出关键工作流备份

## 回滚方案

如果新版本有问题，可以回滚到旧版本：

```bash
# 1. 停止当前容器
docker stop n8n && docker rm n8n

# 2. 拉取指定版本（例如 1.95.0）
docker pull n8nio/n8n:1.95.0

# 3. 运行旧版本
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e N8N_SECURE_COOKIE=false \
  --restart unless-stopped \
  n8nio/n8n:1.95.0
```

## 相关资源

- n8n 官方文档：https://docs.n8n.io/
- Docker Hub: https://hub.docker.com/r/n8nio/n8n
- n8n 版本发布：https://github.com/n8n-io/n8n/releases

## 来源

本技能基于 n8n Docker 部署的标准升级流程创建。
