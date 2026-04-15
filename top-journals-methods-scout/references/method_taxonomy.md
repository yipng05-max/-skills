# 研究方法三层分类体系

这是 skill 在做方法编码时使用的统一分类参照。目标不是穷举——是让不同论文的方法可以相互比较、可以做跨学科统计。

## L1（浅层）：方法家族标签

每篇论文最多归入 2 个 L1 标签，用于 Excel 第一列筛选。

- `qual.ethnography` — 民族志/田野研究（含数字民族志）
- `qual.interview` — 深度访谈/焦点小组
- `qual.case_study` — 案例研究（单案例/多案例比较）
- `qual.historical` — 历史/档案研究
- `qual.discourse` — 话语分析/批评性话语分析
- `qual.narrative` — 叙事研究/生命史
- `qual.grounded` — 扎根理论（经典/程序化/建构主义）
- `qual.thematic` — 主题分析（Braun & Clarke 等）
- `quant.survey` — 问卷调查（横断/面板）
- `quant.experiment` — 实验（实验室/田野/在线/自然）
- `quant.causal_identification` — 因果识别（DID/IV/RDD/合成控制）
- `quant.regression` — 一般回归/多层模型
- `quant.longitudinal` — 纵贯/事件史/生存分析
- `quant.network` — 社会网络分析（ERGM/SAOM 等）
- `comp.text_mining` — 计算文本分析（词频/主题模型/嵌入）
- `comp.simulation` — ABM/仿真模型
- `comp.computational` — 大规模行为数据/数字痕迹
- `ai.llm` — 基于 LLM 的分析方法
- `ai.ml_supervised` — 监督学习建模
- `ai.ml_unsupervised` — 无监督/聚类/降维
- `ai.cv` — 计算机视觉（图像/视频分析）
- `ai.audit` — 算法审计/反事实测试
- `mixed.sequential` — 混合方法（顺序）
- `mixed.concurrent` — 混合方法（并行）
- `review.systematic` — 系统综述/元分析
- `review.scoping` — 范围综述
- `theoretical` — 纯理论/概念建构
- `methodological` — 方法论论文（方法本身是贡献）

若遇到全新方法标签，用 `emerging.<简称>` 临时命名，在 Markdown 报告里专门展开。

## L2（中层）：方法特征字段

每篇论文在 Excel 里用**结构化短语**填这几列，便于筛选：

| 字段 | 取值示例 |
|---|---|
| `data_type` | 访谈转录；问卷；管理数据；Reddit 帖；微博；平台日志；图像；视频；政府档案；报刊；API 抓取数据 |
| `data_source` | 具体平台/机构/数据库（如 Reddit r/xxx、Weibo、GSS、ANES、CGSS） |
| `sample_size` | 定性用 N/案例数；定量用样本量；计算用数据量 |
| `time_window` | 数据覆盖时间段 |
| `geographic_scope` | 国别/区域 |
| `analytic_tools` | NVivo/Atlas.ti/Stata/R/Python/BERT/GPT-4/spaCy/Gephi… |
| `validity_strategy` | 三角验证/成员检验/编码者间信度/稳健性检验/安慰剂检验… |

## L3（深层）：操作流程简述

只在"教学案例候选"论文上填——大约占 10-20%。

一段话（150-300 字）说清楚：
1. 研究问题如何驱动方法选择
2. 数据怎么来的（关键决策点）
3. 分析步骤（从原始材料到结论的跃迁）
4. 本研究独特的方法贡献或变体
5. 可迁移到教学的操作要点

L3 的目的是让课程策划人员直接拿它做教学素材，不是简单复述方法部分。

## 编码原则

- **忠实优先**：不要根据理论倾向脑补方法。如果摘要只说"访谈了 30 位 xx"，就写访谈；不要主动升级为"民族志"。
- **区分方法与数据**：LLM 辅助编码是 `ai.llm` + `qual.*`（取决于研究整体设计），而不是纯 `ai.llm`。混合使用时用两个 L1 标签。
- **存疑标注**：如果摘要信息不足以判断，在相应字段写 `"?"`，并在备注列说明。
- **拒绝贴标签**：遇到理论术语（"批判实在论"之类）不要当方法填入——它们属于认识论，不是方法。
