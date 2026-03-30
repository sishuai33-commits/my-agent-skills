# 安全评估检查清单

评估新 Skill 时，按此清单逐项检查。

---

## 一、文件结构检查

```bash
# 查看 Skill 目录结构
find <skill-path> -type f | head -20
```

**检查项**：
- [ ] 是否有 SKILL.md 或 skill.md（必须有）
- [ ] 是否有可执行脚本（scripts/*.sh, *.py）
- [ ] 是否有配置文件（config.json, .env）
- [ ] 是否有隐藏文件（.开头）

---

## 二、危险模式扫描

### 立即拒绝（P3-高危）

```bash
# 扫描高危模式
grep -rE "curl.*\|.*bash|wget.*\|.*sh|eval\s|exec\s|base64.*--decode|sudo\s" <skill-path>
```

| 模式 | 危险性 | 说明 |
|------|--------|------|
| `curl | bash` | 🔴 极高 | 远程代码执行 |
| `wget -O- | sh` | 🔴 极高 | 远程代码执行 |
| `eval` | 🔴 极高 | 动态代码执行 |
| `exec` | 🔴 极高 | 动态代码执行 |
| `base64 --decode` 后执行 | 🔴 极高 | 代码混淆 |
| `sudo` | 🔴 极高 | 权限提升 |

### 需审查（P2-敏感）

```bash
# 扫描敏感模式
grep -rE "requests\.post|fetch.*POST|axios\.post|\.write|\.append|subprocess|shell=True" <skill-path>
```

| 模式 | 危险性 | 说明 |
|------|--------|------|
| HTTP POST | 🟠 高 | 网络数据发送 |
| 文件写入 | 🟠 高 | 可能覆盖重要文件 |
| subprocess | 🟠 高 | 命令执行 |
| `shell=True` | 🟠 高 | Shell 注入风险 |

### 低风险（P1-受限）

```bash
# 扫描只读模式
grep -rE "requests\.get|fetch|\.read|git.*clone|git.*pull|\.env|process\.env" <skill-path>
```

| 模式 | 危险性 | 说明 |
|------|--------|------|
| HTTP GET | 🟡 中 | 网络请求 |
| 文件读取 | 🟡 中 | 可能读取敏感文件 |
| Git 操作 | 🟡 中 | 网络连接 |
| 环境变量读取 | 🟡 中 | 可能获取密钥 |

---

## 三、敏感路径检查

```bash
# 检查敏感路径引用
grep -rE "~/.ssh|~/.aws|~/.config|/etc/|\.bashrc|\.zshrc|wallet|crypto|private.*key" <skill-path>
```

| 路径 | 危险性 | 说明 |
|------|--------|------|
| `~/.ssh` | 🔴 极高 | SSH 密钥 |
| `~/.aws` | 🔴 极高 | AWS 凭证 |
| `~/.config` | 🟠 高 | 各种配置 |
| `/etc/` | 🔴 极高 | 系统配置 |
| `.bashrc/.zshrc` | 🟠 高 | Shell 配置 |
| `wallet/crypto` | 🔴 极高 | 加密货币 |

---

## 四、SKILL.md 内容审查

**必须阅读** SKILL.md 中的：

1. **name/description**：功能是否合理
2. **使用场景**：触发条件是否明确
3. **执行流程**：具体操作是否安全
4. **配置需求**：是否需要密钥/密码
5. **网络行为**：调用哪些 API

---

## 五、权限等级判定

根据检测结果判定：

```
检测结果 → 权限等级

无任何危险模式 → P0-安全（自动通过）
只有 GET/读取操作 → P1-受限（自动通过）
有 POST/写入/subprocess → P2-敏感（需沙箱）
有高危模式/敏感路径 → P3-高危（立即拒绝）
```

---

## 六、输出评估报告

评估完成后，输出格式：

```
## Skill 安全评估报告

**Skill**: <skill-name>
**来源**: <官方/自建/社区第三方>
**评估时间**: <日期>

### 权限等级: P0/P1/P2/P3

### 检测结果
- 高危模式: X 个
- 敏感模式: X 个
- 只读模式: X 个
- 敏感路径: X 个

### 建议
[批准安装] / [需沙箱测试] / [立即拒绝]

### 注意事项
（如有）
```

---

## 快速评估命令

一键评估脚本：

```bash
# 完整评估
echo "=== 高危模式 ===" && grep -rE "curl.*\|.*bash|eval|exec|sudo" <skill-path> || echo "无"
echo "=== 敏感模式 ===" && grep -rE "requests\.post|\.write|subprocess" <skill-path> || echo "无"
echo "=== 敏感路径 ===" && grep -rE "~/.ssh|~/.aws|/etc/|wallet" <skill-path> || echo "无"
```