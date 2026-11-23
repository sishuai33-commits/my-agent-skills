# 4a-collaborator CHANGELOG

> 版本记录从 SKILL.md 移出（v0.4.0 起）——SKILL.md 是执行指令书，不承载考古地层。

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.7.1 | 2026-11-23 | 细节收口：①规范化 `SKILL.md` frontmatter，将顶层 `category`、`source` 移入 `metadata:` 以通过 `quick_validate.py`；②`references/diagram-handoff.md` 明确 `1.1` 同时支持跨端共享挂载的 `solution-slide-production` 与项目内定制版、`2.1` 补齐 `~/.gemini/config/skills/diagram-design/SKILL.md` 候选路径、`2.3` 明确 `scripts/self_check.py` 属 `diagram-design` 技能目录；③`references/gallery/INDEX.md` 将 `KE-001` 旧路径标为历史本机归档路径，避免误判为活断链。 |
| v0.7.0 | 2026-11-21 | **实战工作流重构（破案找线索 + 陌生域补位 + 全栈双向约束 + 想↔讲压测 + 双轨生图/PPT 交接 + 三层持续成长）**：①`SKILL.md` 删空泛心法，改为 5 个贴身动作（四向找线索与干系人诉求账、陌生域主动补课/反驳/差异路线且严标 `[行业参考/待核估算]`、BA↔AA↔IA↔TA↔硬件算力/网络/部署双向约束链与概念体检、想↔讲双向压测与理想包装补课账/讲后回流、生图交接/看图分流与交付后轻复盘）；触发描述移除“纯画图跳过 4A”；②新增 `references/fullstack-probes.md`（向下探雷触发器、3 分钟陌生域补课法、详设向上挂钩核对）；③升级 `references/diagram-handoff.md` 为双轨——汇报生图→看图分流校准→整套审稿→转可编辑 PPT 主轨（锁轻逻辑约束、不写死像素排版）+ `diagram-design` HTML 副轨，并统一与 methodology 的配色口径；④升级 `references/deliverable-templates.md` 为项目活底座 5 块 + 每页轻逻辑约束卡 + 交付后三栏轻复盘模板；⑤新增中层跨项目复利库 `references/playbooks/`（INDEX + deal-patterns + cross-layer-traps + narrative-arcs），首批从基网智通与一期交付沉淀 10 条实战条目；⑥微修 `huawei-4a-standards.md` 第 15 节 DA→IA 笔误、`diagram-methodology.md` 新增 E 组成套汇报页检查、`gallery/INDEX.md` 去除宿主特定称呼；⑦同步对齐项目内 `solution-slide-production/SKILL.md` 交接边界，并为 Antigravity 补齐 `~/.gemini/config/skills/4a-collaborator` 同源软链。 |
| v0.6.0 | 2026-09-07 | 共同设计成为主线：主动判断/挑战、按问题运用方法、持续决定与纠正记录；撤每轮全流程/全视图要求；新增 diagram-design 本机发现与 HTML 交接、用户风格及真实渲染验收；修正人工承接、目标组件、混层/静态目录/线型语义等冲突。保留既有参考和双端同源入口。 |
| v0.5.0 | 2026-09-03 | **定位重构：从方法论体系到实战工具**。诱因：v0.1-v0.4 理论完备但实战用不上（量子项目实战分叉出简化本地版，全局版闲置）。①**删真源体系**（属性图/伪Cypher投影/状态机/gap工作流——从未落地，纪律替代机制）；②删段1/2/3循环、三能力、档位、活系统等框架包装；③**新主流程**：起手分流（正向设计/逆向梳理/混合）→ 工作底稿（轻量要素表=迭代载体，替代真源）→ 查漏补缺 → 按受众出图 → 待确认清单驱动下轮；④**置信度三档图上标注**（明确=实线/推断=虚线/待确认=标红问号）；⑤**画图层分工**：判断/选图/验收留本 skill，绘制委托 diagram-design，飞书交付走 lark-whiteboard；⑥diagram-methodology.md 瘦身（554→~200行，删视觉语法/工具横评章，移交 diagram-design）；⑦deliverable-templates.md 重写去伪Cypher；⑧五件套降为附录模板；⑨**翻译层泛化**：目标语言按场景定（华为4A/客户术语/中立），不焊死华为；⑩受众颗粒度：一稿多投，L层级×受众定颗粒度；⑪huawei-4a-standards.md 去 Wiki 依赖（自包含，可随 skill 分发）。设计共识：调用时机=头部入口（零散材料→初稿）+尾部兜底（查漏+翻译）；架构图非一蹴而就，底稿养图不养。 |
| v0.4.0 | 2026-07-26 | **结构重构（218→110行）**：①删历史地层（v0.2/v0.3对比表、版本记录移入本文件）；②DRY修复（段1/2/3流程原重复3遍、硬边界原讲3次，合并为一）；③新增**判断层**（画前抽象决策卡：一图一问/受众/刻意不画清单/抽象层级；画后盲读评审）；④**真源与图解耦**（图=图纸target+现状current，不再强制从真源投影；新增gap工作流：里程碑触发、三分类裁决、state字段target/current/both）；⑤段3硬边界措辞修正（现状认真源，规划认段2结论）；⑥修复frontmatter 0.3.1与版本表v0.3.2不一致；⑦画图章节拆解并入主线（原"六、"外挂章删除）；⑧变形适配移入huawei-4a-standards.md；⑨新增references/gallery/案例库。参照：likec4(5.1k⭐模型即真源)/ArchUnit(3.8k⭐规则即测试→gap检测)/FINOS CALM。 |
| v0.3.2 | 2026-07-26 | 画图能力升级：明确关系链路图优先用 DSL + Dagre 自动布局，简单/特殊图用 SVG；diagram-methodology.md 升级 v2.0（第一性原则/12反模式/各图类型权威规则/C4官方checklist融合质量清单，450→554行）。 |
| v0.3.1 | 2026-07-05 | 新增画图能力章节，新增 `references/diagram-methodology.md`。 |
| v0.3.0 | 2026-07-05 | 内核升级真源+4A投影，装进V模型/Y模型/TOGAF价值流/ROMA EAMAP元模型/一体四面/三层数字化。段3硬边界机制化。 |
| v0.2.0 | 2026-07-03 | 范式升级到活系统+五件套+三能力+档位+双轨+多源融合 |
| v0.1.0 | 2026-07-01 | 初始draft。三段式+段3硬边界+渐进状态机+华为硬标准references |
