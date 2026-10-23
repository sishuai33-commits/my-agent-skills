#!/bin/bash
# dp0-gate.sh — 审计前置门禁检查
# 用法: bash dp0-gate.sh <项目路径>
# 退出码: 0 = 通过 / 1 = 拒绝（不满足前置条件）

set -euo pipefail

PROJECT="${1:-$(pwd)}"

echo "=== DP-0 审计前置门禁 ==="
echo "项目: $PROJECT"
echo ""

FAIL=0

# 1. 项目 test 全绿？
echo -n "[1/3] 测试基线... "
if [ -f "$PROJECT/dev/test/run.sh" ]; then
  if bash "$PROJECT/dev/test/run.sh" > /dev/null 2>&1; then
    echo "✅ PASS"
  else
    echo "❌ FAIL (测试未通过或超时)"
    FAIL=1
  fi
elif [ -f "$PROJECT/test/run.sh" ]; then
  if bash "$PROJECT/test/run.sh" > /dev/null 2>&1; then
    echo "✅ PASS"
  else
    echo "❌ FAIL (测试未通过或超时)"
    FAIL=1
  fi
else
  echo "⚠️  SKIP (未找到 test/run.sh 或 dev/test/run.sh)"
fi

# 2. 状态文件最近更新过？
echo -n "[2/3] 状态文件时效... "
STATE=""
for f in "$PROJECT/STATE.md" "$PROJECT/README.md"; do
  [ -f "$f" ] && STATE="$f" && break
done
if [ -n "$STATE" ]; then
  MTIME=$(stat -f %m "$STATE" 2>/dev/null || stat -c %Y "$STATE" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  AGE=$(( (NOW - MTIME) / 86400 ))
  if [ "$AGE" -le 30 ]; then
    echo "✅ PASS ($STATE, ${AGE}天前)"
  else
    echo "⚠️  WARN ($STATE, ${AGE}天前 > 30天)"
  fi
else
  echo "⚠️  SKIP (未找到状态文件)"
fi

# 3. 上次审计 P0 全 closed？
echo -n "[3/3] 上次审计 P0 状态... "
LAST_REPORT=$(find "$PROJECT/audit-reports" -name "tier*.md" -type f 2>/dev/null | sort -r | head -1)
if [ -n "$LAST_REPORT" ]; then
  P0_OPEN=$(grep -c '^\[P0\]' "$LAST_REPORT" 2>/dev/null || echo 0)
  P0_CLOSED=$(grep -c '\[P0\].*closed' "$LAST_REPORT" 2>/dev/null || echo 0)
  if [ "$P0_OPEN" -eq "$P0_CLOSED" ]; then
    echo "✅ PASS (P0: ${P0_OPEN} open / ${P0_CLOSED} closed)"
  else
    OPEN=$((P0_OPEN - P0_CLOSED))
    echo "⚠️  WARN (P0: ${OPEN} 仍 open)"
  fi
else
  echo "⚠️  SKIP (无上次审计报告)"
fi

echo ""
if [ "$FAIL" -eq 1 ]; then
  echo "🔴 DP-0 门禁未通过。请先修复以上 FAIL 项后重试审计。"
  exit 1
else
  echo "🟢 DP-0 门禁通过，可以启动审计。"
  exit 0
fi
