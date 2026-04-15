---
name: top-journals-methods-scout
description: >
  全球人文社科顶刊研究方法扫描与汇总工具。通过 OpenAlex API 抓取社会学、政治学、
  心理学、传播学、管理学、经济学、人类学、教育学、历史学、语言学、地理学、方法论专刊、
  AI-社科交叉期刊、数字人文期刊等 14 大类顶刊近 24 个月（可调）论文，
  对每篇论文做三层深度方法编码（L1 家族标签 / L2 特征字段 / L3 操作简述），
  AI 相关方法单独成章并细分 AI-as-tool 与 AI-as-object，
  输出 Excel 方法矩阵（4 Sheet）+ Markdown 趋势报告（含教学转化建议）。
  面向课程策划人员、研究方法课程教师、研究生方法训练设计者。
  触发条件：用户提到"调研顶刊方法""扫描顶刊研究方法""人文社科方法趋势"
  "最新研究方法汇总""课程方法更新""AI 研究方法扫描""global top journals methods"
  "scan top journals for methods"，或说"帮我看看最近顶刊都用什么方法"、
  "查一下过去两年顶刊的 AI 方法"、"为方法论课程准备最新素材"、
  "全球顶刊最新研究方法调研"。即使用户只是模糊地说"整理最新研究方法"、
  "方法前沿有什么"，只要上下文是学术/教学，也应触发此 skill。
---

# 顶刊研究方法扫描工具（Top Journals Methods Scout）

面向课程策划与方法教学的顶刊方法扫描工具。默认输入：**什么都不说**——
本 skill 会自动用默认的 14 大学科分区顶刊清单 + 近 24 个月 + AI 单独成章。
用户可在第一步选择调整。

## 依赖

```bash
pip install openpyxl
```

OpenAlex API 免费、无需 key；脚本已内置限速。

---

## 第一步：需求确认（≤ 3 问）

向用户确认三件事，用简明清单（**不要**开放问卷式追问）：

1. **学科范围**：默认全部 14 类；是否只要其中几类？
2. **时间窗口**：默认近 24 个月；是否调整为 12/36/48 个月？
3. **AI 聚焦度**：默认 AI 单独成章+常规方法并行；是否纯 AI 方法扫描？

只要用户回一句"默认"就直接进入下一步。

---

## 第二步：执行 OpenAlex 抓取

```bash
python3 /Users/songyiping/.claude/skills/top-journals-methods-scout/scripts/fetch_journal_papers.py \
  --journals-file /Users/songyiping/.claude/skills/top-journals-methods-scout/references/journals.json \
  --months 24 \
  --out /tmp/methods_scout/papers.json
```

如果只要某几个学科，追加 `--disciplines sociology political_science ai_social_intersection`。

输出 `papers.json` 含 meta + papers 数组（每篇含 title/abstract/keywords/concepts/topics 等）。

单次抓取预计 3-10 分钟，取决于学科数量。完成后报告抓取总数与分学科分布。

---

## 第三步：方法编码（三层深度）

对每篇论文做编码。**本步是 skill 的核心**——不能简单喂给 LLM 一股脑处理，
必须按以下规范：

### 3.1 批量化分组

按学科分批（每批 ≤ 30 篇），避免单次编码过载。优先处理 AI 交叉期刊和方法期刊，
因为这两类最可能触发"新兴方法"判断。

### 3.2 编码规范

严格读取以下两个参考文件：

- `references/method_taxonomy.md` — L1/L2/L3 分层说明、L1 标签闭集合
- `references/ai_method_taxonomy.md` — AI-as-tool vs AI-as-object 两大类及子类
- `references/excel_schema.md` — Excel 每个字段的定义与填写规则

对每篇论文输出一条 JSON 记录（字段见 `excel_schema.md` Sheet 1），包括：

- **L1**：1-2 个家族标签（用闭集合）
- **L2**：7 个结构化字段（data_type / data_source / sample_size / time_window_data / geographic_scope / analytic_tools / validity_strategy）
- **AI 专项字段**：ai_involved / ai_category / ai_subcategory / ai_role / ai_model_used / validation_of_ai / ethics_statement / teaching_hook（若 ai_involved=yes）
- **L3**：仅对 `teaching_candidate=yes` 的论文填写 150-300 字操作简述
- **质量门**：teaching_candidate 不得超过论文总数的 20%；methodological_innovation 需有明确理由（不要为了凑数）

### 3.3 输出 classifications.json

```json
{
  "classifications": [
    {
      "openalex_id": "https://openalex.org/Wxxxxx",
      "l1_primary": "qual.ethnography",
      "l1_secondary": "ai.llm",
      "data_type": "访谈转录+AI对话记录",
      ...
      "teaching_candidate": "yes",
      "l3_operational_summary": "..."
    },
    ...
  ]
}
```

保存到 `/tmp/methods_scout/classifications.json`。

### 3.4 质检

编码完成后，简单自查：
- 每篇都有 l1_primary 吗？
- ai_involved=yes 的论文是否都补齐了 AI 专项字段？
- teaching_candidate=yes 的比例是否 ≤ 20%？

---

## 第四步：生成双输出

```bash
python3 /Users/songyiping/.claude/skills/top-journals-methods-scout/scripts/generate_outputs.py \
  --papers /tmp/methods_scout/papers.json \
  --classifications /tmp/methods_scout/classifications.json \
  --journals-file /Users/songyiping/.claude/skills/top-journals-methods-scout/references/journals.json \
  --out-dir /tmp/methods_scout/
```

输出：
- `methods_matrix_<timestamp>.xlsx` —— 4 Sheet 的方法矩阵
- `methods_report_<timestamp>.md` —— 趋势报告骨架（含统计表、待写章节标记）

---

## 第五步：补写 Markdown 报告的分析章节

`generate_outputs.py` 生成的 Markdown 是**骨架**——它自动填好了所有可量化的章节
（L1 频次、学科 × 方法矩阵、AI 统计、期刊覆盖附录、AI 论文附录），
但**留下这些需要主 agent 补写的段落**，以 `_[主 agent 补...]_` 标注：

1. **摘要**（300-500 字）：方法分布全景 + 3 个新动向 + AI 关键形态 + 教学建议
2. **各学科方法画像**（每学科 150-200 字）
3. **新兴方法章节**：按 `report_template.md` 第二章格式，展开 3-6 个新兴方法
4. **AI 专章 3.1/3.2/3.3/3.4**：按子类展开、典型论文一句话、争论点、伦理讨论
5. **教学转化建议 5.1/5.2/5.3**：可直接落地的教学模块
6. **方法缺口**：前瞻性判断

写作要求（遵循 CLAUDE.md 里的学术规范）：
- 禁止套话（"日益重要"、"有助于"、"丰富了"）
- 每个论断都要有论文支撑（给 DOI 或 OpenAlex ID）
- 不虚构数据；不确定时明说
- 教学建议要具体到学时、前置知识、作业原型

参考 `references/report_template.md` 的完整章节规格。

---

## 第六步：向用户交付

最后给用户一个 3-行总结：

```
✓ 扫描完成：N 篇论文，M 本期刊，K 个学科
✓ Excel 方法矩阵：/tmp/methods_scout/methods_matrix_*.xlsx（4 Sheet）
✓ 趋势报告：/tmp/methods_scout/methods_report_*.md
  - 其中 AI 相关 X 篇（tool: X1 / object: X2 / hybrid: X3）
  - 教学候选案例 Y 篇
```

如用户需要可进一步：
- 把 Markdown 转 Word/PDF
- 导出某个子集（只看 AI 方法 / 只看某学科）
- 针对某个新兴方法做 deep-dive（用 `academic-work-analyzer` skill 精读典型论文）

---

## 期刊清单维护

默认清单在 `references/journals.json`，含 14 大学科分区约 50 本顶刊的 ISSN。
如需增减期刊，直接编辑该 JSON。新增期刊时必须包含 ISSN（含 print 和 electronic
两种，OpenAlex 查询时用 `|` 连接）。

已覆盖的层级（tier）：
- `top` — 各学科公认顶刊
- `methods` — 方法论专刊
- `ai_intersect` — AI 与社科交叉期刊
- `dh` — 数字人文期刊
- `review` — 综述期刊

---

## 设计哲学

1. **默认优先**：课程策划者通常不想先设计检索策略，skill 提供可立即运行的默认
2. **三层分层**：浅（L1 标签，可统计）→ 中（L2 字段，可筛选）→ 深（L3 操作，可教学迁移），深度递减但信息密度递增
3. **AI 分类严肃**：区分 "用 AI 研究" 与 "研究 AI" ——这两者教学含义完全不同
4. **可量化骨架 + 主 agent 叙事**：Python 做不会错的统计表和附录，主 agent 做需要判断的分析章节——各自做最擅长的事
5. **教学转化是一等公民**：每个新兴方法都要落到"这能教吗？怎么教？"

---

## 常见调整

- 用户要聚焦中国社科：暂无内置中文期刊；可合 `cnki-advanced-search` skill 做 C 刊补充
- 用户要特定主题（如"LLM 研究中的方法"）：可以先 fetch 再在编码阶段过滤关键词
- 用户要比较两个时期：分别跑两次 fetch（不同 months 参数），合并时加 `period` 字段
