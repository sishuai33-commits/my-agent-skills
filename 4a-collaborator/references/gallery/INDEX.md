# Gallery：优秀图案例库

> **入库纪律：无批注不入库。** 只收图不收"为什么好"，这里就是图片坟场。
> 每条目 = 图（链接/快照）+ 图类型 + 为什么好（对标 diagram-methodology.md 原则）+ 可复用模式。
> v2.1（2026-11-21）：整理跨宿主中性表述；含 27 正面 + 8 正误对照；快照存 snapshots/；文件存在不证明格式有效或来源完整，使用前核格式与内容，外链可用性另核。

## 收集机制（三通道）

| 通道 | 来源 | 频率 | 质量 |
|------|------|------|------|
| **1. 用户投喂**（主力） | 工作中遇到的好图/烂图 → 丢链接或截图 → 批注入库 | 随时 | 最高（真实场景） |
| **2. 批量检索**（慢环） | 在线库定向检索 → 筛选批注 | 按需 | 中高 |
| **3. 实战复盘** | 自己每次画图迭代的对比版本（失败→修复） | 每次画图后 | 高（教训最新鲜） |

**烂图也收**：标注"踩了哪个反模式"（对标 methodology 第二章 12 反模式），与正面教材 **pair 绑定**（同来源正误对照教学效果最好）。

## 三维标签（检索用）

- **布局模式**：分层 / zoom / 泳道 / 嵌套盒 / 箭头链 / 生命线 / 网格
- **抽象层级**：Context / L1 / L2 / 物理级
- **标注风格**：编号流 / 图例 / 价值项表 / 正误对照 / 决策说明

---

## 1. DFD 数据流图

| 编号 | 图名 | 为什么好 / 可复用模式 | 链接 |
|------|------|---------------------|------|
| DFD-01 | Yourdon/DeMarco 入门（Visual Paradigm） | 4 元素记号讲透，配图干净；记号入门样本 | [link](https://blog.visual-paradigm.com/beginners-guide-to-yourdon-demarco-dfd-diagrams/) |
| DFD-02 | DFD 分层教程（Lucidchart） | Context→L1→L2 递进最标准示范；附四结构规则原文。**教学 pair**：同页反面（黑洞/奇迹过程/外部实体直连存储） | [link](https://lucid.co/diagram/dfd/tutorial) |
| DFD-03 | L1 DFD 模板（Lucidchart） | **L1 粒度教科书**：过程居中、存储和实体靠边——直接对治我们 v3 版"塞太多"的病 | [link](https://lucid.co/templates/data-flow-diagram-level-1) |
| DFD-04 | Online Store DFD（ConceptDraw） | 完整业务 DFD，外部实体与数据流标注清晰，配色克制 | [link](https://www.conceptdraw.com/examples/yourdon-and-demarco) |

## 2. C4 模型架构图

| 编号 | 图名 | 为什么好 / 可复用模式 | 链接 |
|------|------|---------------------|------|
| C4-01 | Big Bank plc 全套（官网） | **C4 标准答案**：同系统四层 zoom、自动图例、颜色语义一致（蓝=内部/灰=外部） | [link](https://c4model.com) |
| C4-02 | Structurizr 官方示例工作区 | **"一个模型生成多张图"的一致性活样板**——真源+投影同构，可交互验证 | [link](https://www.structurizr.com/public/1) |
| C4-03 | System Context 示例+DSL（dotnet 文档） | 图+代码并排；Context"只画人和系统、不画技术细节"的抽象纪律 | [link](https://github.com/structurizr/dotnet/blob/master/docs/system-context-diagram.md) |
| C4-04 | C4 示例索引（6 系统） | 一页收齐不同领域的 C4 全套，横向比较同方法在不同系统的应用 | [link](https://frameworks.readthedocs.io/en/latest/framework/C4ModelNote.html) |
| C4-05 ⚠️ | NCSC 正误对照资料（本地快照无效） | 2026-11-16核查：本地`.pdf`实际保存的是HTML 404页，不能作为已取得教材或配图的证据；旧教材描述待回源确认，未联网复核原链接。保留失败文件供追溯，不当作PDF使用。 | `snapshots/ncsc-drawing-good-architecture-diagrams.pdf`（无效） + [原链接待核](https://www.ncsc.gov.uk/pdfs/blog-post/drawing-good-architecture-diagrams.pdf) |

## 3. 泳道流程图 / BPMN

| 编号 | 图名 | 为什么好 / 可复用模式 | 链接 |
|------|------|---------------------|------|
| BPMN-01 | Camunda Examples（同场景 3 解法） | **建模决策教学最佳范例**：同一业务场景 3 种建模方案+优劣对比——直接喂 skill 判断层。**教学 pair**：同页反例 Avoid Crossing Flows + 命名反例 | [link](https://camunda.com/bpmn/examples/) |
| BPMN-02 | Camunda 符号参考（披萨订购协作图） | Pool/Lane/消息流/折叠池标准画法；跨组织泳道图范本 | [link](https://camunda.com/en/bpmn/reference/) |
| BPMN-03 | HEFLO 5 个泳道实例 | 2→6 泳道梯度实例；lane 按"角色"非"人名"命名（Silver 风格） | [link](https://www.heflo.com/blog/bpm/swim-lane-diagram-examples/) |
| BPMN-04 | bpmn-for-research（GitHub） | **3700+ 图的正误对比训练集**：习题/学员答案/标准答案三件套——可直接用作"画后盲读评审"的练兵场 | [link](https://github.com/camunda/bpmn-for-research) |

## 4. ER 图（Crow's Foot）

| 编号 | 图名 | 为什么好 / 可复用模式 | 链接 |
|------|------|---------------------|------|
| ER-01 | ERD 教程+符号图解（Lucidchart） | Chen/Crow's Foot/Bachman/IDEF1X/Barker 五记号并排对比+鸦爪基数逐个拆解——记号选型与识读一站齐 | [教程](https://lucid.co/diagram/erd/tutorial) / [符号](https://lucid.co/diagram/erd/symbols-and-notation) |
| ER-02 | Pawnshop ERD（VP 社区） | 当铺完整 ERD，实体多但不乱——中等复杂度 ER 排版学习样本 | [link](https://online.visual-paradigm.com/community/share/pawnshop-erd-crow-s-foot--1nj01nfnwf) |
| ER-03 ⚠️ | Northeastern CS3200 讲义 | **教学 pair**：多对多不拆关联实体、漏画主键——"don't forget identifiers" | snapshots/northeastern-...pdf + [link](https://northeastern-datalab.github.io/cs3200/fa22s3/download/cs3200-L11-Design.pdf) |

## 5. 业务能力地图

| 编号 | 图名 | 为什么好 / 可复用模式 | 链接 |
|------|------|---------------------|------|
| CAP-01 | LeanIX 5 行业能力地图 | **"嵌套盒+热力着色"最佳示范**：同一结构跨 5 行业套用，L1→L3 嵌套盒标准范式 | [link](https://www.leanix.net/en/wiki/ea/business-capability-map-examples-and-templates) |
| CAP-02 | LeanIX 最佳实践样例 | 应用映射到能力的双层视图（能力框内嵌应用）——业务-IT 对齐一目了然 | [link](https://www.leanix.net/en/sap-leanix-business-capability-map) |
| CAP-03 | Orbus 4 种形态对比 | 能力树/矩阵/热力图/嵌套盒一页对比——"同一模型多种视图"教学 | [link](https://www.orbussoftware.com/resources/wiki/article/business-capability-mapping) |
| （反） | LeanIX 8 条禁令 | 能力重叠（L2 无法唯一归 L1=边界错）+ 按组织架构画能力（how/who 当 what） | 同 CAP-01/02 |

## 6. 价值流图

| 编号 | 图名 | 为什么好 / 可复用模式 | 链接 |
|------|------|---------------------|------|
| VS-01 | TOGAF Value Streams 官方指南 | **官方范式原图**：阶段箭头链+每阶段进出条件/价值项表+阶段-能力热力图（图1/3/4）。**教学 pair**：附录 A 正误对照（画成 Lean 流程图/波特价值链=错位） | snapshots/togaf-...pdf + [link](https://governance.foundation/assets/frameworks/togaf/g178_2%20-%20Value%20Streams.pdf) |
| VS-02 | VSM 保险/新产品开发（VP Guides） | 价值流与能力映射结合实例；Develop New Product 五阶段动宾命名规范 | [link](https://guides.visual-paradigm.com/value-stream-mapping-artifact-of-vision-phase/) |

## 7. 云部署/技术架构图

| 编号 | 图名 | 为什么好 / 可复用模式 | 链接 |
|------|------|---------------------|------|
| CLOUD-01 | AWS 官方参考架构库 | 官方图标体系+VPC/AZ/子网嵌套边界的行业标准画法；数百张可下载 | [link](https://aws.amazon.com/architecture/reference-architecture-diagrams/) |
| CLOUD-02 | Azure App Service baseline | **"编号数据流（1→2→3）+Well-Architected 决策说明"模板级示范**——图不只是图，还带每条流的决策依据 | [link](https://learn.microsoft.com/en-us/azure/architecture/web-apps/web-apps-get-started) |
| CLOUD-03 | GCP three-tier + Terraform | 架构图与 Terraform 代码一一对应——"架构图即可部署"典范 | [link](https://github.com/GoogleCloudPlatform/terraform-google-three-tier-web-app) |
| CLOUD-04 | 阿里云《云原生架构白皮书》 | 中文标杆：特步/斯凯奇中台四层架构图，中文分层架构图参考 | [link](https://www.jiagou.com/public/990x/9902.%E4%BA%91%E5%8E%9F%E7%94%9F%E6%9E%B6%E6%9E%84%E7%99%BD%E7%9A%AE%E4%B9%A6.pdf) |
| （反） | diagrams.so AWS 三错 | 单 AZ（图暴露单点）/RDS 放公网/ALB 前无 WAF——**部署图特殊价值：图会暴露架构缺陷**，评审时顺手查 | [link](https://diagrams.so/blog/aws-architecture-diagram-best-practices) |

## 8. UML 时序图

| 编号 | 图名 | 为什么好 / 可复用模式 | 链接 |
|------|------|---------------------|------|
| SEQ-01 | uml-diagrams.org 经典例图 | Facebook OAuth 跨系统认证时序=万能范本；alt/loop 组合片段用法标准 | [link](https://www.uml-diagrams.org/sequence-diagrams-examples.html) |
| SEQ-02 | Creately 时序图教程+7 条最佳实践 | **教学 pair**：第一条即最常见错误"一张图塞进所有对象"——一图一场景、能放进一页留注释空间 | [link](https://creately.com/guides/sequence-diagram-tutorial/) |
| SEQ-03 | Lucidchart 时序图教程 | 生命线/激活条/同步异步箭头规范示范 | [link](https://lucid.co/diagram/uml/sequence-diagram-tutorial) |

---

## 自产实战案例

### KE-001 · ke DFD v3 → Dagre 迭代对比（2026-07-25/26）

- **来源**：自家实战，~/diagrams/2026-07-25T221500/（v2/v3 手调 SVG）+ ~/diagrams/2026-07-26T100000/（Dagre 版 JSON）
- **图类型**：DFD L1
- **为什么好（修复后）**：
  - v3 失败版踩中反模式 #1 God Diagram + #2 Boxes&Lines Soup + #7 Mixed Abstractions：112 节点塞入所有辅助存储/回灌线/质量监督线，L1 画成 L2
  - 修复路径印证 methodology 原则 2（认知负荷）：辅助存储下沉 L2、回灌合并为一条、质量监督改文字标注 → 节点降到可读密度
  - Dagre 版 0 errors 无重叠，印证"布局正确 > 视觉美感"
- **可复用模式**：
  - DFD L1 的**刻意不画清单**实例：辅助存储（D5/D6/D7）不画、回灌细节不画、监督线不画
  - "先 Dagre 出拓扑骨架，再决定是否精修"的两阶段流程
- **快照/链接**：~/diagrams/2026-07-26T100000/dfd-ke-l1-dagre.json；飞书画板 https://acnhcoyajo3n.feishu.cn/docx/KmRId9JIvomV25xIvuFcwqKAn9e

---

## 待扩充

- [ ] 中文精品：腾讯云架构中心、华为云架构图库（当前仅 CLOUD-04 一个中文）
- [ ] 页面型案例快照：模板社区链接失效风险高，用到时先抓快照存 snapshots/
- [ ] 华为 4A 交付件真实案例（随真实项目脱敏投喂）
