---
name: huashu-flash
description: 针对网站或 App 的首屏、交互响应和加载速度开展实测优化；定义可用时刻、测量基线、配对比较并防止性能回退。仅性能任务使用，不为普通改动自动建立完整性能治理。
metadata:
  source_path: /Users/sishuai/Documents/My_Skills_Library/社区第三方/huashu-flash
  adapted_for: Codex
  source_version: 'git@94a06d0'
  adapted_on: '2026-10-10'
---

# 性能优化

复用 CC/Pi huashu-flash 的基准脚本和测量协议（MIT），以用户真正能操作的时刻作为目标。references 和 scripts 为共享只读资源；测试结果写进目标项目，不改技能原件。

1. 从需求与工程确定慢的页面/动作、何时算可用、不能破坏的行为，以及本次范围/停止条件。能从已有上下文得到的不重复询问。不替用户默认设定性能减半目标。
2. 定义可复现的 ready 表达式（必要时实际输入或点击验证），读 `references/measurement-protocol.md`。占位与不可交互的骨架不算就绪。
3. 用 `scripts/bench.py` 建基线；先检查已安装的 Playwright 和浏览器，勿自动安装。基准记录设备、宽度、缓存、网络/CPU条件、失败次数与 p50/p75/p95。小样仅验证工具，不据此宣称性能改善。
4. 按改动的实际风险设置功能、内容与视觉检查，以 `scripts/ratchet.py` 保存关键指标上限。真实耗时需容差；确定性计数可用零容差。脚本的 check 即使不带 --update 也会重写同内容上限文件，使用项目内专用文件。
5. 每次只改一个可解释的瓶颈；按需读 `references/playbook.md`。代理指标必须和用户实际等待时间建立证据关系。失败的改动只撤销本次差异，不覆盖他人工作。
6. 对实质提速结论，用同一时段 A/B 交替配对各至少 10 次测量；正式报告记录 ready 表达式、条件、样本、失败与离散情况。不可把不同条件下的数字直接比较。
7. 达到约定目标、后续收益不足或本轮预算用尽时收尾，避免无期限优化。上线/推送沿用用户已有授权；未获授权时交付可审查的本地修改与测量证据。

常用调用（S 是本技能绝对路径）：

```sh
python3 "$S/scripts/bench.py" --url http://127.0.0.1:8000 --url-b http://127.0.0.1:8001 --ready "!!document.querySelector('button:not([disabled])')" --runs 10 --out perf/paired.json
python3 "$S/scripts/ratchet.py" init --result perf/base.json --ceilings perf/ceilings.json
python3 "$S/scripts/ratchet.py" check --result perf/after.json --ceilings perf/ceilings.json
```

结果目录随项目规范；`references/brief-template.md` 是可裁剪的模板。没有线上数据就说未覆盖，不能由本地实测推出所有真实用户都变快。
