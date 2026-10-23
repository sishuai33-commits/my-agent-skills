#!/bin/bash
# audit-marker.sh — ke-audit 持久标记管理
# 用法:
#   bash audit-marker.sh mark <file> <severity> <desc> <verify-cmd>
#   bash audit-marker.sh check <project-path>
#   bash audit-marker.sh close <file> <marker-id>

set -euo pipefail

MARKER_PREFIX="ke-audit"

cmd_mark() {
  local file="$1" severity="$2" desc="$3" verify="$4"
  local date=$(date +%Y-%m-%d)
  local marker="# ${MARKER_PREFIX}(${severity},${date}): ${desc}"
  local verify_line="#   验证: ${verify}"

  if [ ! -f "$file" ]; then
    echo "❌ 文件不存在: $file"
    exit 1
  fi

  # 检查是否已有相同标记
  if grep -q "${MARKER_PREFIX}(${severity},${date}): ${desc}" "$file" 2>/dev/null; then
    echo "⚠️  标记已存在: $file"
    return 0
  fi

  # 在文件末尾追加标记
  echo "" >> "$file"
  echo "$marker" >> "$file"
  echo "$verify_line" >> "$file"
  echo "✅ 已标记: $file ($severity)"
}

cmd_check() {
  local project="${1:-$(pwd)}"
  echo "=== ke-audit 标记扫描 ==="
  echo "项目: $project"
  echo ""

  local total=0 closed=0 recurred=0

  # 扫描所有包含 ke-audit 标记的文件
  while IFS=: read -r file line_num content; do
    total=$((total + 1))

    # 提取严重度、日期、描述
    severity=$(echo "$content" | grep -oP "${MARKER_PREFIX}\(\K[^,]+" || echo "??")
    date=$(echo "$content" | grep -oP "${MARKER_PREFIX}\([^,]+, \K[^)]+" || echo "????-??-??")
    desc=$(echo "$content" | sed "s/.*${MARKER_PREFIX}([^)]*): //" || echo "??")

    # 找下一条验证行
    verify_line=$(sed -n "$((line_num + 1))p" "$file" | grep "^#   验证:" | sed 's/^#   验证: //' || echo "")

    if [ -n "$verify_line" ]; then
      # 跑验证命令
      if eval "$verify_line" > /dev/null 2>&1; then
        status="✅ closed"
        closed=$((closed + 1))
      else
        status="🔴 recurred"
        recurred=$((recurred + 1))
      fi
    else
      status="⚠️  no-verify"
    fi

    printf "  [%s] %s:%s — %s (%s)\n" "$severity" "$file" "$line_num" "$desc" "$status"
  done < <(grep -rn "${MARKER_PREFIX}(" "$project" --include="*.py" --include="*.sh" --include="*.js" --include="*.md" 2>/dev/null || true)

  echo ""
  echo "总计: $total | closed: $closed | recurred: $recurred"

  if [ "$recurred" -gt 0 ]; then
    echo "🔴 $recurred 条复发，需关注"
  elif [ "$total" -eq 0 ]; then
    echo "（无 ke-audit 标记）"
  else
    echo "🟢 全部 closed"
  fi
}

cmd_close() {
  local file="$1" marker_id="$2"

  if [ ! -f "$file" ]; then
    echo "❌ 文件不存在: $file"
    exit 1
  fi

  # 在标记行后追加 closed 状态
  sed -i "" "s/${MARKER_PREFIX}(${marker_id})/${MARKER_PREFIX}(${marker_id},closed)/" "$file" 2>/dev/null || \
  sed -i "s/${MARKER_PREFIX}(${marker_id})/${MARKER_PREFIX}(${marker_id},closed)/" "$file"
  echo "✅ 已标 closed: $file ($marker_id)"
}

case "${1:-}" in
  mark)   shift; cmd_mark "$@" ;;
  check)  cmd_check "${2:-$(pwd)}" ;;
  close)  shift; cmd_close "$@" ;;
  *)
    echo "用法:"
    echo "  audit-marker.sh mark <file> <severity> <desc> <verify-cmd>"
    echo "  audit-marker.sh check [project-path]"
    echo "  audit-marker.sh close <file> <marker-id>"
    exit 1
    ;;
esac
