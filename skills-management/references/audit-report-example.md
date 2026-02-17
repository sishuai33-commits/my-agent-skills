# 安全审查报告示例

**Skill 名称**: example-skill  
**审查时间**: 2026-02-16 14:30:00  
**审查人**: Claude Code  
**审查模式**: 完整（含沙箱）

## 文件结构

```
/Users/sishuai/.../clawhub-pending/example-skill/
├── SKILL.md
├── scripts/
│   ├── main.py
│   └── utils.sh
└── assets/
    └── template.txt
```

## 危险模式检查

- ✅ 未发现高危代码模式

## 敏感路径检查

- ✅ 未发现敏感路径访问

## 网络行为检查

- ⚠️ 发现网络请求代码
  - 使用 `requests.get()` 调用外部 API
  - API 端点: https://api.example.com

## 权限分级建议

- ⚠️ **P2-敏感**
- **理由**: 网络请求 + 文件写入
- **建议**: 需要沙箱测试和详细审查

## SKILL.md 预览

```markdown
# Example Skill

This skill fetches data from API and saves to local file...
```

## Docker 沙箱测试

```
=== 文件类型检查 ===
SKILL.md: ASCII text
scripts/main.py: Python script
scripts/utils.sh: Bourne-Again shell script
```

## 审查结论

**权限等级**: P2-敏感

**统计数据**:
- 高危模式: 0
- 敏感路径: 0
- 网络请求: 是

## 建议操作

⚠️ **需要审查** - 此 Skill 需要敏感权限，建议:
1. 仔细阅读 SKILL.md
2. 在沙箱环境中测试功能
3. 确认 API 调用目的合理性

**批准命令**:
```bash
~/.scripts/clawhub-fetch.sh approve example-skill
```

**拒绝命令**:
```bash
~/.scripts/clawhub-fetch.sh reject example-skill
```

---
*报告由 security-audit.sh 自动生成*
