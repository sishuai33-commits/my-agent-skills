# 技能更新速查

一页纸。跑检查、读结果、动手升级，都在这。

## 一条命令

```bash
~/Documents/My_Skills_Library/技能库_自建/skills-management/scripts/skills-check.sh
# 离线（不联网，只看本地 origin 引用）
.../skills-check.sh --no-fetch
# 隔离测试（自定义发现根）
SKILLS_ROOTS=/tmp/x:y .../skills-check.sh
```

退出码：`0` 全部可核且无变化（含无上游本地项）/ `2` 有更新 / `3` 含未知 / `1` 脚本自身错。更新与未知并存返回 `3`，汇总同时保留 `updates=1 unknown=1`。联网 fetch 会更新远端引用，但不改工作区、不升级。

## 什么时候跑

- `ai-maintenance` 做体检时
- 任务中发现某技能行为不对、文档与实现不符
- 装新技能或升级任何技能之前

**不设定时**。这是事件触发，不是周期巡检。

## 三种结果怎么读

| 组 | 长什么样 | 含义 | 处置 |
|---|---|---|---|
| **A. git 仓** | `UNCHANGED` / `BEHIND` / `CACHED` / `UNKNOWN` | fetch 成功才可核当前；离线计数只是缓存，fetch 失败不能报同步 | BEHIND 按授权升级；UNKNOWN 先补证据 |
| **B. 有档案** | `UNCHANGED` / `CONTENT_CHANGED` / `VERSION_CHANGED` / `UNKNOWN` | 始终比 sha256；有版本时同时比版本。缺哈希基准为未知 | 变化需人工比对；版本不同不自动证明版本更高 |
| **C. 盲区** | 只有路径 | 非 git 且无档案 | 补 `UPSTREAM.md`，否则永远不知道上游变了 |

几个状态别搞混：

- `🏠 本地仓无上游` / `🏠 自建/本地真源` —— 正常，自己写的东西没有上游可追
- `UNKNOWN` —— 网络/鉴权/地址、无远端分支、缺基准或离线未取证；既不证明落后，也不证明同步。`CACHED` 仅描述已缓存引用，即使显示零落后也保持 unknown。
- `dirty=N` —— 工作区未提交改动，升级前必须先处理

## 升级流程（git 仓）

```bash
# 1. 先看本地有没有未提交改动
git -C <repo> status --porcelain

# 2. 有本地口径改动：先存补丁，再 stash
git -C <repo> diff > /backup/<name>.patch
git -C <repo> stash push -m "local <date>"

# 3. 只允许快进
git -C <repo> pull --ff-only origin <branch>

# 4. 叠回本地口径，冲突就手工解
git -C <repo> stash pop

# 5. 本地提交，不留脏工作区（否则下次 pull 会被拒）
git -C <repo> add <files> && git -C <repo> commit -m "chore: 本地口径叠加到 <version>"
```

**有本地定制提交时**：用 `git rebase origin/main`，不要 `merge`，也不要用上游覆盖。合完逐文件核对本地治理字段（`category`/`source`/`metadata`）还在不在。

## 提取式安装（没有 git 的）怎么升

```bash
cd /tmp && rm -rf up && git clone --depth 1 <repo> up
# 1. 先看本地有没有上游没有的文件——有就先捞出来，别被 --delete 删掉
comm -23 <(ls <本地>/assets | sort) <(ls /tmp/up/<子目录>/assets | sort)
# 2. 整目录替换，排除自己的档案
rsync -a --delete --exclude 'UPSTREAM.md' /tmp/up/<子目录>/ <本地>/
# 3. 回叠本地口径（版本号、§0 覆盖块之类）
# 4. 校验 SKILL.md 里引用的每个 references/*.md 都存在
```

## 新装一个提取式技能时，当场做三件事

1. 写 `UPSTREAM.md`：上游地址、安装版本、本地改了什么、下次怎么升
2. 加一行机器可读记录，否则 B 组报「仅档案未登记检查」：

```html
<!-- skills-check: upstream=<上游 SKILL.md 的 raw 地址> version=<本地版本> sha256=<该文件 sha256> checked=<日期> -->
```

3. 同目录多技能时用 `skill=<技能名>` 区分

`sha256` 取法：`curl -fsSL <url> -o /tmp/x && shasum -a 256 /tmp/x`

## 改脚本时踩过的两个坑

| 坑 | 现象 | 正确做法 |
|---|---|---|
| 哈希基准 | 对 `body=$(curl ...)` 的变量算 sha256，永远对不上 | 命令替换会剥掉**尾部换行**，必须 `curl -o 文件` 后 `shasum` 文件 |
| 变量边界 | `$up_ver（档案记…）` 报 `unbound variable` | 中文紧跟变量时 bash 会把 UTF-8 首字节吃进变量名，统一写 `${up_ver}` |

验证脚本改动：运行 `python3 -m unittest discover -s tests -v`（本技能目录），使用临时根和 fake git/curl；覆盖 fetch 失败、离线缓存、同版本变哈希、缺基准、取不到、本地无上游，以及更新+未知双标识。不对真实仓库 fetch。

## 已知边界

- **单独 clone `技能库_自建`**：`codex-adapters` 的相对软链会断，它依赖同级 `社区第三方/` 与 `anthropic_官方/`。整库一起搬才行。
- **B 组依赖网络**：取不到时报 UNKNOWN、退出 3，不误判为落后或全绿。
- **上游改内容不升版本号**：版本相同仍比 sha256；基准缺失则 UNKNOWN，不能据此报内容未变。
