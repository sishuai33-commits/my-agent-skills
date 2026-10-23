#!/bin/bash
# tier2-run.sh — project-audit Tier 2 轻量对抗审查入口
# 用法: bash tier2-run.sh <项目路径>
# CC 在对话中调用此脚本后，应按其输出的指令派 agent 执行审查

set -euo pipefail

PROJECT="${1:-$(pwd)}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_DIR="$PROJECT/audit-reports"
mkdir -p "$REPORT_DIR"

DATE=$(date +%Y-%m-%d)
REPORT="$REPORT_DIR/tier2-${DATE}.md"

echo "=== project-audit Tier 2 轻量对抗审查 ==="
echo "项目: $PROJECT"
echo "报告: $REPORT"
echo ""

# DP-0 前置
echo ">>> 步骤 1/3: DP-0 前置门禁"
bash "$SKILL_DIR/scripts/dp0-gate.sh" "$PROJECT"
echo ""

# Scope Fence
echo ">>> 步骤 2/3: Scope Fence 范围声明"
echo "审计范围: $PROJECT"
echo "排除: .git/ node_modules/ __pycache__/ *.pyc"
echo ""

# 输出审查指令给 CC
echo ">>> 步骤 3/3: 派 agent 执行审查"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 请在对话中执行以下两步（可并行）："
echo ""
echo "1. 派 agent-1（代码审查）:"
echo "   类型: code-reviewer"
echo "   加载: $SKILL_DIR/prompts/code-quality.md"
echo "   路径: $PROJECT"
echo ""
echo "2. 派 agent-2（诚实性标注）:"
echo "   类型: general-purpose"
echo "   加载: $SKILL_DIR/prompts/honesty-check.md"
echo "   路径: $PROJECT"
echo ""
echo "3. 合并两个 agent 的输出 → 去重 → P0/P1/P2 分类"
echo "   → 每个发现带一行验证命令 → 写入 $REPORT"
echo ""
echo "4. 若 P0 ≥ 3 或上次 Tier 3 > 14 天: 建议升 Tier 3"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查上次 Tier 3 时间
LAST_T3=$(find "$REPORT_DIR" -name "tier3-*.md" -type f 2>/dev/null | sort -r | head -1)
if [ -n "$LAST_T3" ]; then
  T3_MTIME=$(stat -f %m "$LAST_T3" 2>/dev/null || stat -c %Y "$LAST_T3" 2>/dev/null)
  T3_AGE=$(( ($(date +%s) - T3_MTIME) / 86400 ))
  echo ""
  echo "⚠️  提醒: 上次 Tier 3 在 ${T3_AGE} 天前 (>= 14 天建议升级)"
fi
