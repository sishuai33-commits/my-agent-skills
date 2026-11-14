#!/usr/bin/env bash
# skills-check.sh — 技能上游更新检查（不升级、不改工作区；联网 fetch 会更新远端引用）
#
# 用法：
#   ./skills-check.sh            # 联网：对每个 git 仓 fetch 后比对
#   ./skills-check.sh --no-fetch # 离线：只用本地已有的 origin/* 引用比对
#
# 输出三组：
#   A. git 仓      —— 能精确到提交，落后会标 ❌
#   B. 有来源档案   —— 非 git，同时比对 UPSTREAM.md 的版本和内容哈希
#   C. 盲区        —— 非 git 也无来源记录，无法判断是否有新版本
#
# 退出码：0 全部可核且无变化（含无上游本地项）；2 有更新；3 含未知；1 自身错误
# 更新+未知返回 3，汇总同时保留 updates=1 unknown=1。

set -uo pipefail

FETCH=1
case "${1:-}" in
  "") ;;
  --no-fetch) FETCH=0 ;;
  *) echo "用法：$0 [--no-fetch]" >&2; exit 1 ;;
esac
[ "$#" -le 1 ] || exit 1
for cmd in git awk sort grep sed shasum mktemp; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "缺少必要命令：$cmd" >&2; exit 1; }
done
if [ "$FETCH" -eq 1 ]; then
  command -v curl >/dev/null 2>&1 || { echo "缺少必要命令：curl" >&2; exit 1; }
fi

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
[ "$FETCH" -eq 1 ] || echo "模式：离线（git 仅缓存引用；当前上游未知）"
echo

backlog=0
unknown=0
[ "$total" -gt 0 ] || unknown=1

# ---------- 3. A 组：git 仓 ----------
echo "═══ A. 可追踪上游的 git 仓 ═══"
printf "%-26s %-10s %5s %5s %6s  %s\n" "仓库" "状态" "落后" "领先" "未提交" "技能"
echo "--------------------------------------------------------------------------------"
awk -F'\t' '$1!="-"{print $1}' "$TMP/map.tsv" | sort -u > "$TMP/repos.list"
while read -r repo; do
  name=$(basename "$repo")
  skills=$(awk -F'\t' -v r="$repo" '$1==r{printf "%s ", $2}' "$TMP/map.tsv" | sed 's/ $//')
  br=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
  dirty=$(git -C "$repo" status --porcelain 2>/dev/null | grep -vc '^??' || true)
  behind="-"; ahead="-"
  remotes=$(git -C "$repo" remote 2>/dev/null); remote_rc=$?
  if [ "$remote_rc" -ne 0 ]; then
    st="UNKNOWN 远端配置不可读"; unknown=1
  elif [ -z "$remotes" ]; then
    st="🏠 本地仓无上游"
  elif ! printf '%s\n' "$remotes" | grep -qx origin; then
    st="UNKNOWN 未配置 origin"; unknown=1
  elif [ "$FETCH" -eq 1 ] && ! git -C "$repo" fetch --quiet origin 2>/dev/null; then
    st="UNKNOWN fetch失败（网络/鉴权），缓存不证明当前同步"; unknown=1
  elif git -C "$repo" rev-parse --verify "origin/$br" >/dev/null 2>&1; then
    cnt=$(git -C "$repo" rev-list --left-right --count "origin/$br...HEAD" 2>/dev/null) || cnt=""
    if [[ "$cnt" =~ ^[0-9]+[[:space:]]+[0-9]+$ ]]; then
      read -r behind ahead <<< "$cnt"
      if [ "$behind" -gt 0 ]; then
        st="BEHIND 落后"; backlog=1
      else
        st="UNCHANGED 已含上游"
      fi
    else
      st="UNKNOWN 提交计数失败"; unknown=1
    fi
    if [ "$FETCH" -eq 0 ]; then
      st="CACHED ${st}；当前上游 UNKNOWN"; unknown=1
    fi
  else
    st="UNKNOWN 无可用远端分支"; unknown=1
  fi
  printf "%-26s %-10s %5s %5s %6s  %s\n" "$name" "$st" "$behind" "$ahead" "$dirty" "$skills"
done < "$TMP/repos.list"

# ---------- 4. B/C 组：非 git ----------
awk -F'\t' '$1=="-"{print $2"\t"$3}' "$TMP/map.tsv" > "$TMP/nongit.tsv"
if [ -s "$TMP/nongit.tsv" ]; then
  echo
  echo "═══ B. 非 git，按档案比对上游 ═══"
  : > "$TMP/blind.tsv"
  while IFS=$'\t' read -r name real; do
    doc=""
    [ -f "$real/UPSTREAM.md" ] && doc="$real/UPSTREAM.md"
    [ -z "$doc" ] && [ -f "$(dirname "$real")/UPSTREAM.md" ] && doc="$(dirname "$real")/UPSTREAM.md"
    if [ -z "$doc" ]; then
      printf "%s\t%s\n" "$name" "$real" >> "$TMP/blind.tsv"
      unknown=1
      continue
    fi
    if ! grep -q 'skills-check:' "$doc" && grep -qE '自建|本地真源|无上游' "$doc"; then
      printf "  %-32s %s\n" "$name" "🏠 自建/本地真源"
      continue
    fi
    rec=$(grep -o '<!-- skills-check:[^>]*-->' "$doc" 2>/dev/null | grep "skill=$name" | head -1)
    [ -z "$rec" ] && rec=$(grep -o '<!-- skills-check:[^>]*-->' "$doc" 2>/dev/null | grep -v 'skill=' | head -1)
    if [ -z "$rec" ]; then
      src=$(grep -m1 -oE 'https?://[^ )）,，]+' "$doc" | head -1)
      printf "  %-32s %s\n" "$name" "UNKNOWN 仅档案未登记检查（${src:-无地址}）"
      unknown=1
      continue
    fi
    url=$(printf '%s' "$rec" | sed -n 's/.*upstream=\([^ ]*\).*/\1/p')
    rec_ver=$(printf '%s' "$rec" | sed -n 's/.*version=\([^ ]*\).*/\1/p')
    rec_sum=$(printf '%s' "$rec" | sed -n 's/.*sha256=\([^ ]*\).*/\1/p')
    if [ "$FETCH" -eq 0 ]; then
      printf "  %-32s %s\n" "$name" "UNKNOWN 离线跳过，档案不是当前上游证据"
      unknown=1
      continue
    fi
    if [[ ! "$url" =~ ^https?:// ]]; then
      printf "  %-32s %s\n" "$name" "UNKNOWN 缺少有效上游地址"
      unknown=1
      continue
    fi
    # 注意：必须落盘再算哈希。$(...) 命令替换会剥掉尾部换行，直接对变量算 sha256 永远对不上。
    tf="$TMP/up-$name.md"
    if ! curl -fsSL --max-time 30 --retry 2 --retry-delay 1 "$url" -o "$tf" 2>/dev/null || [ ! -s "$tf" ]; then
      printf "  %-32s %s\n" "$name" "UNKNOWN 上游取不到/空响应（网络/鉴权/地址），非已证实落后"
      unknown=1
      continue
    fi
    up_ver=$(grep -m1 -E '^[[:space:]]*version:' "$tf" | sed "s/.*version:[[:space:]]*//;s/[\"']//g;s/[[:space:]]*$//")
    changed=0; item_unknown=0
    if [ -n "$rec_ver" ]; then
      if [ -z "$up_ver" ]; then
        printf "  %-32s %s\n" "$name" "UNKNOWN 无法读取上游版本"
        item_unknown=1
      elif [ "$rec_ver" != "$up_ver" ]; then
        printf "  %-32s %s\n" "$name" "VERSION_CHANGED 上游 ${up_ver}（档案 ${rec_ver}），需判断升级方向"
        changed=1
      fi
    fi
    if [[ ! "$rec_sum" =~ ^[[:xdigit:]]{64}$ ]]; then
      printf "  %-32s %s\n" "$name" "UNKNOWN 缺少有效 sha256 基准；同版本不能证明内容未变"
      item_unknown=1
    else
      cur=$(shasum -a 256 "$tf" | awk '{print $1}') || { echo "哈希计算失败" >&2; exit 1; }
      rec_sum=$(printf '%s' "$rec_sum" | tr '[:upper:]' '[:lower:]')
      if [ "$cur" != "$rec_sum" ]; then
        printf "  %-32s %s\n" "$name" "CONTENT_CHANGED 上游内容已变（即使版本相同），需人工比对"
        changed=1
      fi
    fi
    [ "$changed" -eq 0 ] || backlog=1
    [ "$item_unknown" -eq 0 ] || unknown=1
    if [ "$changed" -eq 0 ] && [ "$item_unknown" -eq 0 ]; then
      printf "  %-32s %s\n" "$name" "UNCHANGED 内容哈希一致，已登记版本一致（如有）"
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
echo "汇总：updates=$backlog unknown=$unknown"
if [ "$unknown" -eq 1 ]; then
  echo "结论：含未知/缓存项，不能判定全绿；已确认变化另见 BEHIND/CONTENT_CHANGED/VERSION_CHANGED。"
  exit 3
fi
if [ "$backlog" -eq 1 ]; then
  echo "结论：存在已确认的落后或上游变化，需审查，不自动升级。"
  exit 2
fi
echo "结论：全部已检查项可核且未发现上游变化（本地无上游项正常）。"
exit 0
