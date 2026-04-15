# Excel 输出字段规范

本 skill 输出的 Excel 文件含 4 个 Sheet。字段严格按以下表定义，便于跨批次数据合并。

## Sheet 1: `methods_matrix`（方法矩阵主表）

一行一篇论文。列顺序不可调整。

| 列名 | 说明 | 示例 |
|---|---|---|
| `paper_id` | 行号（001, 002 ...） | 001 |
| `journal` | 期刊名 | American Sociological Review |
| `discipline` | 学科键 | sociology |
| `tier` | 期刊层级 | top / methods / ai_intersect / dh / review |
| `publication_date` | 出版日期 | 2025-06-15 |
| `title` | 论文标题 | |
| `authors` | 作者列表（分号分隔） | |
| `doi` | DOI | |
| `cited_by_count` | OpenAlex 被引 | 12 |
| `l1_primary` | L1 主方法标签 | qual.ethnography |
| `l1_secondary` | L1 次方法标签（可空） | ai.llm |
| `data_type` | 数据类型 | 访谈转录 |
| `data_source` | 数据来源 | Reddit r/ChatGPT |
| `sample_size` | 样本量/案例数/数据规模 | N=42 |
| `time_window_data` | 数据覆盖时段 | 2022-2024 |
| `geographic_scope` | 地理范围 | 美国东海岸 |
| `analytic_tools` | 分析工具 | NVivo 14; Claude 3.5 |
| `validity_strategy` | 效度策略 | 三角验证；编码者间信度 |
| `ai_involved` | 是否涉及 AI | yes / no |
| `ai_category` | AI 类别 | tool / object / hybrid / n/a |
| `ai_subcategory` | AI 子类 | llm_coding / algorithmic_audit / ... |
| `methodological_innovation` | 是否方法论创新 | yes / no |
| `teaching_candidate` | 是否教学案例候选 | yes / no |
| `l3_operational_summary` | L3 操作流程简述（仅 teaching_candidate=yes 时填写） | 150-300 字 |
| `notes` | 编码者备注/存疑 | |

## Sheet 2: `ai_papers`（AI 专项表）

仅包含 `ai_involved = yes` 的论文，字段比主表精简，便于 AI 子领域分析。

| 列名 |
|---|
| paper_id / journal / discipline / title / doi |
| ai_category / ai_subcategory |
| ai_role（AI 在研究中的具体角色，一句话） |
| ai_model_used（GPT-4 / Claude / BERT / 自训练…） |
| validation_of_ai（如何验证 AI 产出可信度） |
| ethics_statement（是否有伦理声明，简述） |
| teaching_hook（一句话：可用来教什么） |

## Sheet 3: `by_discipline_summary`（学科汇总）

每学科一行。列：

- discipline
- n_papers
- top_3_l1_methods（频次降序）
- n_ai_papers
- ai_percentage
- n_methodological_innovations
- n_teaching_candidates
- disciplinary_notes（一句话总评）

## Sheet 4: `journals_meta`（期刊元数据）

每期刊一行，用于追溯覆盖情况。

- journal / abbr / issn / discipline / tier
- n_papers_in_window
- date_range_of_papers
- skipped_reason（如果该期刊本期无数据，写原因）

---

## 编码质量要求

1. **不要空列**：所有列必填；无信息时写 `"?"` 或 `"n/a"`，不要留空字符串。
2. **L1 标签闭集合**：只用 `method_taxonomy.md` 定义的标签，除非确认是全新方法（用 `emerging.*` 前缀）。
3. **AI 标签一致性**：`ai_involved=no` 时，`ai_category`/`ai_subcategory` 必须为 `n/a`。
4. **教学候选不超过 20%**：不要给每篇论文都打 `teaching_candidate=yes`。只给方法最清晰、最易迁移的打。
5. **L3 简述避免复述摘要**：它要的是"这个方法怎么被做出来"，不是"研究发现了什么"。
