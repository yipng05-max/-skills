---
name: top-journals-methods-scout
description: >
  全球人文社科顶刊研究方法扫描与汇总工具。通过 OpenAlex API 抓取社会学、政治学、
  心理学、传播学、管理学、经济学、人类学、教育学、历史学、语言学、地理学、方法论专刊、
  AI-社科交叉期刊、数字人文期刊等 14 大类顶刊近 24 个月（可调）论文，
  用启发式规则做大规模方法打标 + AI 识别（L1 家族标签，可处理万篇级），
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
本 skill 会自动用 14 大学科分区顶刊清单 + 近 24 个月 + AI 单独成章。

## 设计现实（先读这段）

第一次试跑时低估了数据规模——14 个学科分区近 24 个月的顶刊发文约 **10,000 篇**（AHR/Q&Q 等刊发文量大是主因）。对 10k 篇做逐篇 LLM 深度编码既不经济也不必要。因此本 skill 的**实际主路径**是：

1. **启发式规则编码**（`heuristic_classify.py`）——对全库打 L1 家族标签 + AI 识别，覆盖快
2. **Python 生成统计骨架**（`generate_outputs.py`）——Excel 矩阵 + Markdown 自动统计章节
3. **主 agent 写分析层**（补一份 `methods_report_analysis.md`）——用启发式统计做依据，写摘要、新兴方法、AI 专章、教学模块建议

LLM 深度编码只用于特定子集（如用户聚焦某学科、或对某 50 篇做教学候选精选）。

## 依赖

```bash
pip install openpyxl
```

OpenAlex API 免费、无需 key；脚本已内置重试限速。

---

## 第一步：需求确认（≤ 3 问）

用简明清单向用户确认（**不要**开放问卷式追问）：

1. **学科范围**：默认全部 14 类；是否只要其中几类？
2. **时间窗口**：默认近 24 个月；是否调整为 12/36/48 个月？
3. **AI 聚焦度**：默认 AI 单独成章 + 常规方法并行；是否纯 AI 方法扫描？

用户回"默认"就直接下一步。

**向用户坦诚成本**：全学科 24 个月扫约 10k 篇，抓取 5-10 分钟、启发式编码 1 分钟、统计生成 10 秒、分析写作由主 agent 完成。总耗时约 15-20 分钟。

---

## 第二步：OpenAlex 抓取

```bash
mkdir -p /tmp/methods_scout
python3 /Users/songyiping/.claude/skills/top-journals-methods-scout/scripts/fetch_journal_papers.py \
  --journals-file /Users/songyiping/.claude/skills/top-journals-methods-scout/references/journals.json \
  --months 24 \
  --out /tmp/methods_scout/papers.json
```

只要某几个学科追加 `--disciplines sociology ai_social_intersection ...`。

脚本已内置指数退避重试（5 次），网络抖动不会中断。单次抓取 5-10 分钟。完成后报告总数与分学科分布。

---

## 第三步：启发式方法编码（主路径）

```bash
python3 /Users/songyiping/.claude/skills/top-journals-methods-scout/scripts/heuristic_classify.py \
  --papers /tmp/methods_scout/papers.json \
  --out /tmp/methods_scout/classifications.json
```

内置规则（详见 `scripts/heuristic_classify.py` 里的 `METHOD_RULES` 与 `AI_OBJECT_RULES`）：
- 扫 title + abstract + keywords + concepts + topics 的拼接文本
- 按规则优先级匹配 L1 标签（AI 方法先于普通方法以保证 LLM 辅助定性研究正确识别）
- AI 识别：tool（用 AI）/ object（研究 AI）/ hybrid / n/a
- 输出包含规则命中证据片段（在 `notes` 列）

**编码结果典型特征：**
- 未匹配率 60-75%（人文历史论文摘要通常不写方法）——正常
- AI 识别率通常 5-10%
- L1 分布最常见：qual.ethnography / qual.interview / ai.llm / quant.experiment / quant.survey

**不需要** LLM 逐篇编码。如果用户后续要求对某子集做深度编码，再调 LLM（见 §补充路径）。

---

## 第四步：生成 Excel + Markdown 骨架

```bash
python3 /Users/songyiping/.claude/skills/top-journals-methods-scout/scripts/generate_outputs.py \
  --papers /tmp/methods_scout/papers.json \
  --classifications /tmp/methods_scout/classifications.json \
  --journals-file /Users/songyiping/.claude/skills/top-journals-methods-scout/references/journals.json \
  --out-dir /tmp/methods_scout/
```

产物：
- `methods_matrix_<timestamp>.xlsx` —— 4 Sheet 矩阵（methods_matrix / ai_papers / by_discipline_summary / journals_meta）
- `methods_report_<timestamp>.md` —— 自动统计骨架（含 L1 频次、学科×方法、AI 子类分布、期刊覆盖、AI 论文完整附录）

Excel 可独立使用，用 Sheet 筛选就能回答大多数"哪篇用什么方法"的问题。

---

## 第五步：主 agent 写分析层报告

这一步是**主 agent 核心贡献**——Python 输出的是骨架，读者要的是判断。

**重要**：不要直接编辑 Python 生成的 MD（它是可重生的统计产物）。
**而是**新建一份 `/tmp/methods_scout/methods_report_analysis.md`，独立承载分析叙事。

### 5.1 抽样核验

用一段 Python 快速捞几个 ai_subcategory 下的高被引论文（含标题/期刊/DOI/被引/摘要开头），这些将是报告引用的"骨头"。示例：

```python
python3 << 'EOF'
import json
from collections import defaultdict
with open('/tmp/methods_scout/papers.json') as f:
    papers = {p['openalex_id']: p for p in json.load(f)['papers']}
with open('/tmp/methods_scout/classifications.json') as f:
    cs = {c['openalex_id']: c for c in json.load(f)['classifications']}

groups = defaultdict(list)
for oid, c in cs.items():
    if c['ai_involved'] != 'yes':
        continue
    p = papers[oid]
    groups[(c['ai_category'], c['ai_subcategory'])].append(
        (p['cited_by_count'], p['title'], p['journal'], p['doi'])
    )
for k, v in sorted(groups.items()):
    v.sort(reverse=True)
    print(f"\n{k} — {len(v)} 篇")
    for cited, t, j, d in v[:4]:
        print(f"  [{cited}] {j}: {t[:100]}")
        print(f"    {d}")
EOF
```

同时看方法刊高被引（`tier_map[journal]=='methods' and cited>=5`）——这批论文往往就是"新兴方法"的代表。

### 5.2 写作规范

报告结构（参考 `/tmp/methods_scout/methods_report_analysis.md` 已有实例）：

1. **执行摘要**（300-500 字）
   - 最强信号、三条带分布、AI 方法画像、给课程策划的 2-3 条直接建议
2. **新兴方法扫描**（3-6 个）
   - 每个：频次信号、代表论文（含被引+DOI）、方法内核、与既有方法关系、边界条件、教学转化指向
3. **AI 方法专章**
   - 2.1 AI-as-tool 总览（子类分布 + 典型论文）
   - 2.2 AI-as-object 总览（子领域分析）
   - 2.3 Hybrid 类
   - 2.4 AI 方法的伦理与效度挑战（以"审稿常见质疑"形式）
4. **方法论文专栏**
   - 方法期刊中方法本身即贡献的论文，表格呈现
5. **方法缺口**（面向未来 12-24 个月）
   - 识别顶刊里**没见到**但应该有的——这是预测性分析
6. **教学转化建议（核心）**
   - 5.1 可立即上线的模块 —— 每个模块含：教学目标、前置知识、核心阅读（2024-2026 顶刊论文 + 被引数 + DOI）、操作任务（作业原型，一句话）、课时、风险提示
   - 5.2 已有课程更新点（表格：现有课程 | 删除 | 新增）
   - 5.3 跨院系共建建议
7. **数据局限性**（务必诚实）
8. **深挖切入点**（5 篇"必读" + 5 篇"次读"）

### 5.3 语言红线（CLAUDE.md 规定）

- 禁止套话（"日益重要"、"有助于"、"丰富了"）
- 每个论断要有论文支撑（给 DOI 或被引数）
- 不虚构数据；不确定时明说
- 教学建议要具体到学时、前置知识、作业原型
- 中文学术写作，书面化但不僵化，拒绝八股文风

### 5.4 目标长度

约 300-500 行 Markdown（8,000-12,000 字中文）。太短说明没真吃数据；太长说明在堆砌。

---

## 第六步：向用户交付

给用户一个 5-行总结：

```
✓ 扫描完成：N 篇论文，M 本期刊，K 个学科
✓ Excel 方法矩阵：/tmp/methods_scout/methods_matrix_*.xlsx（4 Sheet）
✓ 统计骨架：/tmp/methods_scout/methods_report_*.md
✓ 分析报告：/tmp/methods_scout/methods_report_analysis.md  ← 先看这份
  - AI 相关 X 篇（tool: X1 / object: X2 / hybrid: X3）
  - 识别 N 个新兴方法，拟 M 个可上线教学模块
```

然后提供后续可选动作：
- 转 Word/PDF
- 复制到桌面避免 /tmp 被清
- 对某篇关键论文深挖（用 `academic-work-analyzer`）
- 把 skill 改进推 GitHub

---

## 补充路径：小批量深度编码（可选）

如果用户明确要求对某子集做深度 LLM 编码（比如"把 50 篇教学候选论文全部写 L3 操作简述"），流程：

1. 在 Excel 里筛出目标子集（比如 `teaching_candidate=yes`，或手动挑选）
2. 读取每篇的 title/abstract/keywords 做 LLM 深度编码（填充 data_type/sample_size/time_window_data/geographic_scope/analytic_tools/validity_strategy 等 L2 字段 + L3 操作简述）
3. 合并回 `classifications.json`，重跑 `generate_outputs.py`

这一步没有脚本自动化——因为需要语境判断，适合主 agent 直接读 JSON 后输出增强版 classifications。

---

## 期刊清单维护

默认清单在 `references/journals.json`，含 14 大学科分区约 50 本顶刊的 ISSN。
如需增减期刊，直接编辑该 JSON。新增期刊时必须包含 ISSN（含 print 和 electronic
两种，OpenAlex 用 `|` 连接查询）。

已覆盖的层级（tier）：
- `top` — 各学科公认顶刊
- `methods` — 方法论专刊
- `ai_intersect` — AI 与社科交叉期刊
- `dh` — 数字人文期刊
- `review` — 综述期刊

---

## 常见调整

- **聚焦中国社科**：本 skill 无中文期刊；可接 `cnki-advanced-search` skill 做 C 刊补充
- **特定主题扫描**（如"LLM 研究方法"）：先 fetch 再在 `heuristic_classify.py` 输出后按关键词过滤 `papers.json` 的 abstract
- **比较两个时期**：分别跑两次 fetch（不同 months 参数），合并时加 `period` 字段
- **Quality & Quantity 论文过多**：该刊 862 篇、应用型为主，方法创新比例低于 SMR。筛选时注意此刊样本质量参差——建议在 Excel 里按 `tier=methods AND cited>=5` 过滤获得高信号子集

---

## 设计哲学

1. **启发式优先、LLM 备选**：10k 规模逼出的现实选择——规则快、可追溯、覆盖广
2. **Python 做统计、agent 做叙事**：骨架可重生、叙事需判断，分工清晰
3. **AI 分类严肃**：区分 "用 AI" 与 "研究 AI"，两者教学含义完全不同
4. **教学转化是一等公民**：每个新兴方法都要落到"这能教吗？怎么教？"
5. **诚实承认局限**：71% 未匹配是真实状况，不要装作完美覆盖
