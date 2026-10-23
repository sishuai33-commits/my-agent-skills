#!/usr/bin/env bash
# skills-check.sh — 技能上游更新检查（只读，不升级、不改文件）
#
# 用法：
#   ./skills-check.sh            # 联网：对每个 git 仓 fetch 后比对
#   ./skills-check.sh --no-fetch # 离线：只用本地已有的 origin/* 引用比对
#
# 输出三组：
#   A. git 仓      —— 能精确到提交，落后会标 ❌
#   B. 有来源档案   —— 非 git，但有 UPSTREAM.md 记录上游，需人工比对
#   C. 盲区        —— 非 git 也无来源记录，无法判断是否有新版本
#
# 退出码：0 正常；2 发现落后；1 脚本自身出错

set -uo pipefail

FETCH=1
[ "${1:-}" = "--no-fetch" ] && FETCH=0

# 可用 SKILLS_ROOTS="路径1:路径2" 覆盖，便于隔离测试
if [ -n "${SKILLS_ROOTS:-}" ]; then
  IFS=':' read -r -a ROOTS <<< "$SKILLS_ROOTS"
else
  ROOTS=( "$HOME/.claude/skills" "$HOME/.agents/skills" )
fi
TMP=$(mktemp -d) || exit 1
trap 'rm -rf "$TMP"' EXIT

# ---------- 1. 收集已装技能，按真实路径去重 ----------
: > "$TMP/skills.tsv"
for root in "${ROOTS[@]}"; do
  [ -d "$root" ] || continue
  for d in "$root"/*; do
    [ -e "$d" ] || continue
    real=$(cd "$d" 2>/dev/null && pwd -P) || continue
    [ -f "$real/SKILL.md" ] || continue
    printf "%s\t%s\n" "$real" "$(basename "$d")" >> "$TMP/skills.tsv"
  done
done
awk -F'\t' '!seen[$1]++' "$TMP/skills.tsv" > "$TMP/skills.uniq"
total=$(wc -l < "$TMP/skills.uniq" | tr -d ' ')

# ---------- 2. 技能归仓 ----------
: > "$TMP/map.tsv"
while IFS=$'\t' read -r real name; do
  top=$(git -C "$real" rev-parse --show-toplevel 2>/dev/null)
  printf "%s\t%s\t%s\n" "${top:--}" "$name" "$real" >> "$TMP/map.tsv"
done < "$TMP/skills.uniq"

echo "技能总数（去重后）：$total"
echo "检查时间：$(date '+%Y-%m-%d %H:%M')"
[ "$FETCH" -eq 1 ] || echo "模式：离线（未 fetch）"
echo

backlog=0

# ---------- 3. A 组：git 仓 ----------
echo "═══ A. 可追踪上游的 git 仓 ═══"
printf "%-26s %-10s %5s %5s %6s  %s\n" "仓库" "状态" "落后" "领先" "未提交" "技能"
echo "--------------------------------------------------------------------------------"
awk -F'\t' '$1!="-"{print $1}' "$TMP/map.tsv" | sort -u > "$TMP/repos.list"
while read -r repo; do
  name=$(basename "$repo")
  skills=$(awk -F'\t' -v r="$repo" '$1==r{printf "%s ", $2}' "$TMP/map.tsv" | sed 's/ $//')
  [ "$FETCH" -eq 1 ] && git -C "$repo" fetch --quiet origin 2>/dev/null
  br=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
  dirty=$(git -C "$repo" status --porcelain 2>/dev/null | grep -vc '^??' || true)
  if [ -z "$(git -C "$repo" remote 2>/dev/null)" ]; then
    behind="-"; ahead="-"; st="🏠 本地仓无上游"
  elif git -C "$repo" rev-parse --verify "origin/$br" >/dev/null 2>&1; then
    cnt=$(git -C "$repo" rev-list --left-right --count "origin/$br...HEAD" 2>/dev/null || echo "? ?")
    behind=$(echo "$cnt" | awk '{print $1}'); ahead=$(echo "$cnt" | awk '{print $2}')
    if git -C "$repo" merge-base --is-ancestor "origin/$br" HEAD 2>/dev/null; then
      st="✅ 同步"; [ "${behind:-0}" != "0" ] && st="✅ 已含上游"
    else
      st="❌ 落后"; backlog=1
    fi
  else
    behind="-"; ahead="-"; st="⚠️ 无远端分支"
  fi
  printf "%-26s %-10s %5s %5s %6s  %s\n" "$name" "$st" "$behind" "$ahead" "$dirty" "$skills"
done < "$TMP/repos.list"

# ---------- 4. B/C 组：非 git ----------
awk -F'\t' '$1=="-"{print $2"\t"$3}' "$TMP/map.tsv" > "$TMP/nongit.tsv"
if [ -s "$TMP/nongit.tsv" ]; then
  echo
  echo "═══ B. 非 git，但有来源档案（需人工比对）═══"
  : > "$TMP/blind.tsv"
  while IFS=$'\t' read -r name real; do
    doc=""
    [ -f "$real/UPSTREAM.md" ] && doc="$real/UPSTREAM.md"
    [ -z "$doc" ] && [ -f "$(dirname "$real")/UPSTREAM.md" ] && doc="$(dirname "$real")/UPSTREAM.md"
    if [ -n "$doc" ]; then
      if grep -qE '自建|本地真源|无上游' "$doc"; then
        printf "  %-32s %s\n" "$name" "🏠 自建/本地真源"
      else
        src=$(grep -m1 -oE 'https?://[^ )）,，]+' "$doc" | head -1)
        printf "  %-32s %s\n" "$name" "${src:-（档案未写上游地址）}"
      fi
    else
      printf "%s\t%s\n" "$name" "$real" >> "$TMP/blind.tsv"
    fi
  done < "$TMP/nongit.tsv"
  if [ -s "$TMP/blind.tsv" ]; then
    echo
    echo "═══ C. 盲区：非 git 且无来源档案，无法判断 ═══"
    while IFS=$'\t' read -r name real; do
      printf "  %-32s %s\n" "$name" "$real"
    done < "$TMP/blind.tsv"
    echo "  → 补法：在该技能目录写 UPSTREAM.md（上游地址 + 安装版本 + 升级方法）"
  fi
fi

echo
if [ "$backlog" -eq 1 ]; then
  echo "结论：存在落后上游的 git 仓，见 A 组 ❌ 行。"
  exit 2
fi
echo "结论：没有发现落后上游的 git 仓。"
