#!/usr/bin/env python3
"""
基于关键词规则的启发式方法编码器。

用途：对大规模论文库（本 skill 场景下 ~10k 篇顶刊论文）做 L1 家族标签 + AI 识别，
       替代不可行的逐篇 LLM 编码。输出可直接喂给 generate_outputs.py。

设计原则：
  - 宁可保守：规则要求匹配明确关键词，不硬猜
  - 可追溯：所有规则命中记录在 notes 列
  - 自动 AI 识别：严格区分 AI-as-tool（方法学采用）vs AI-as-object（研究对象）

用法：
  python3 heuristic_classify.py \
    --papers /tmp/methods_scout/papers.json \
    --journals-file /path/to/journals.json \
    --out /tmp/methods_scout/classifications.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# 规则定义：(l1_tag, regex_pattern)
# 顺序即优先级：越靠前越优先匹配
# ---------------------------------------------------------------------------

METHOD_RULES: list[tuple[str, re.Pattern]] = [
    # AI methods（需要在普通方法之前识别，因为 LLM 辅助常与 qual 方法并存）
    ("ai.llm",            re.compile(r"\b(large language model|LLMs?|GPT-?[34o]?|ChatGPT|Claude|"
                                     r"transformer[- ]based|BERT|RoBERTa|prompt engineering|"
                                     r"prompt[- ]based|generative (?:AI|model))", re.I)),
    ("ai.cv",             re.compile(r"\b(computer vision|image classification|image recognition|"
                                     r"convolutional neural network|CNN[- ]based|"
                                     r"street[- ]view image|satellite imag)", re.I)),
    ("ai.ml_supervised",  re.compile(r"\b(supervised (?:machine )?learning|random forest|"
                                     r"gradient boost|XGBoost|neural network (?:classifier|model)|"
                                     r"support vector machine|SVM classifier)", re.I)),
    ("ai.ml_unsupervised",re.compile(r"\b(unsupervised learning|k-means|DBSCAN|HDBSCAN|"
                                     r"hierarchical cluster|word embedding|sentence embedding|"
                                     r"UMAP|t-SNE)", re.I)),
    ("ai.audit",          re.compile(r"\b(algorithmic audit|algorithm auditing|audit stud(?:y|ies) of "
                                     r"(?:algorithm|platform|AI|machine)|platform audit)", re.I)),

    # Computational
    ("comp.text_mining",  re.compile(r"\b(topic model(?:ling|ing)?|LDA|latent dirichlet|"
                                     r"text mining|computational text analysis|"
                                     r"sentiment analysis|NLP pipeline)", re.I)),
    ("comp.simulation",   re.compile(r"\b(agent-based (?:model|simulation)|ABM|"
                                     r"microsimulation|multi-agent simulation)", re.I)),
    ("comp.computational",re.compile(r"\b(computational social science|digital trace data|"
                                     r"web scraping|log data analysis|big data analys)", re.I)),

    # Quant
    ("quant.experiment",  re.compile(r"\b(randomi[sz]ed controlled trial|RCT|"
                                     r"field experiment|lab(?:oratory)? experiment|"
                                     r"survey experiment|online experiment|"
                                     r"vignette experiment|conjoint experiment)", re.I)),
    ("quant.causal_identification",
                          re.compile(r"\b(difference[- ]in[- ]differences?|DiD analysis|"
                                     r"instrumental variable|regression discontinuity|RDD|"
                                     r"synthetic control|propensity score matching|"
                                     r"natural experiment|quasi-experiment)", re.I)),
    ("quant.longitudinal",re.compile(r"\b(event history analys|survival analys|"
                                     r"duration model|cox proportional|"
                                     r"longitudinal panel|growth curve model)", re.I)),
    ("quant.network",     re.compile(r"\b(social network analys|network analysis|ERGM|"
                                     r"exponential random graph|SAOM|stochastic actor-oriented|"
                                     r"bipartite network)", re.I)),
    ("quant.survey",      re.compile(r"\b(survey data|survey respondents?|questionnaire|"
                                     r"panel survey|nationally representative sample|"
                                     r"(?:GSS|ANES|CGSS|ESS|WVS|CFPS)\b)", re.I)),
    ("quant.regression",  re.compile(r"\b(multilevel model|hierarchical linear model|HLM|"
                                     r"fixed[- ]effects (?:model|regression)|"
                                     r"mixed[- ]effects model|logistic regression|"
                                     r"OLS regression)", re.I)),

    # Qualitative
    ("qual.ethnography",  re.compile(r"\b(ethnograph(?:y|ic)|participant observ|"
                                     r"field(?:work| research| observations)|"
                                     r"digital ethnograph|virtual ethnograph|"
                                     r"autoethnograph)", re.I)),
    ("qual.interview",    re.compile(r"\b(in-depth interview|semi-?structured interview|"
                                     r"qualitative interview|focus group|"
                                     r"\d{1,3} interviews?|interviewed \d{1,3})", re.I)),
    ("qual.grounded",     re.compile(r"\b(grounded theory|open coding|axial coding|"
                                     r"constant comparison|theoretical sampling)", re.I)),
    ("qual.thematic",     re.compile(r"\b(thematic analysis|Braun and Clarke|"
                                     r"reflexive thematic)", re.I)),
    ("qual.discourse",    re.compile(r"\b(discourse analysis|critical discourse|CDA|"
                                     r"conversation analysis)", re.I)),
    ("qual.narrative",    re.compile(r"\b(narrative analysis|narrative inquiry|"
                                     r"life history|life story|biographical interview)", re.I)),
    ("qual.case_study",   re.compile(r"\b(case study|case-study|comparative case|"
                                     r"multiple-case|single-case|embedded case)", re.I)),
    ("qual.historical",   re.compile(r"\b(archival research|archival analys|archive data|"
                                     r"historical sociology|historical analys|"
                                     r"historiograph)", re.I)),

    # Mixed / review / theoretical
    ("mixed.sequential",  re.compile(r"\b(mixed[- ]methods? (?:design|approach|research)|"
                                     r"sequential explanatory|sequential exploratory)", re.I)),
    ("review.systematic", re.compile(r"\b(systematic review|meta-analys|PRISMA|"
                                     r"scoping review|integrative review|"
                                     r"bibliometric (?:analys|review))", re.I)),
    ("theoretical",       re.compile(r"\b(conceptual (?:paper|framework|model)|"
                                     r"theoretical (?:paper|framework|model)|"
                                     r"theory-building|we (?:propose|develop|advance) a "
                                     r"(?:theory|framework|model))", re.I)),
    ("methodological",    re.compile(r"\b(we propose (?:a|the) (?:method|approach|technique|"
                                     r"estimator|algorithm)|new method for|"
                                     r"methodological (?:contribution|innovation|advance))", re.I)),
]

# AI-as-object 识别规则（研究 AI 本身）
# 核心模式：paper 把 AI/算法/LLM/平台算法当成被研究的现象
AI_OBJECT_RULES: list[re.Pattern] = [
    re.compile(r"\b(bias|discriminat\w+|fairness) (?:in|of) "
               r"(?:algorithm|AI|machine learning|LLM|ChatGPT|GPT|model)", re.I),
    re.compile(r"\b(?:algorithm|AI|LLM|ChatGPT|GPT|model) (?:bias|discriminat\w+|fairness)", re.I),
    re.compile(r"\b(how (?:users?|workers?|people|consumers?) (?:perceive|experience|"
               r"interact with|resist) (?:AI|algorithm|ChatGPT|LLM|platform))", re.I),
    re.compile(r"\b(ghost work|data (?:labeler|annotator)s?|content moderator)", re.I),
    re.compile(r"\b(algorithmic (?:audit|accountability|governance|management|"
               r"discrimination|bias))", re.I),
    re.compile(r"\b(platform (?:labor|work|capitalism|power|governance))", re.I),
    re.compile(r"\b(AI (?:governance|policy|regulation|ethics|accountability|discourse))", re.I),
    re.compile(r"\b(studying (?:the|an|a) (?:algorithm|AI|LLM|model|chatbot))", re.I),
]

# 简单的"AI 相关"兜底（抓出那些 METHOD_RULES 没匹到但确实与 AI 有关的）
AI_GENERAL_RULE = re.compile(
    r"\b(artificial intelligence|machine learning|deep learning|"
    r"generative AI|AI system|AI-driven|AI-based|chatbot|LLM)",
    re.I,
)

# AI 子类映射（AI-as-tool 时用）
AI_TOOL_SUBCAT = {
    "ai.llm": "llm_text_analysis",
    "ai.cv": "computer_vision",
    "ai.ml_supervised": "supervised_ml",
    "ai.ml_unsupervised": "unsupervised_ml",
    "ai.audit": "algorithmic_audit",
}

# ---------------------------------------------------------------------------


def build_text(p: dict) -> str:
    """拼出待匹配文本：title + abstract + keywords + concepts + topics"""
    parts = [
        p.get("title", ""),
        p.get("abstract", ""),
        p.get("keywords", ""),
        p.get("concepts", ""),
        p.get("topics", ""),
    ]
    return " \n ".join(str(x) for x in parts if x)


def classify_one(p: dict) -> dict:
    text = build_text(p)
    matches: list[tuple[str, str]] = []  # (tag, evidence_snippet)
    for tag, pat in METHOD_RULES:
        m = pat.search(text)
        if m:
            matches.append((tag, m.group(0)[:60]))

    # 去重且保持顺序
    seen: set[str] = set()
    uniq: list[tuple[str, str]] = []
    for tag, ev in matches:
        if tag in seen:
            continue
        seen.add(tag)
        uniq.append((tag, ev))

    l1_primary = uniq[0][0] if uniq else "?"
    l1_secondary = uniq[1][0] if len(uniq) > 1 else ""

    # AI 识别
    ai_tags_hit = [t for t, _ in uniq if t.startswith("ai.")]
    general_ai = bool(AI_GENERAL_RULE.search(text))
    object_hit = any(r.search(text) for r in AI_OBJECT_RULES)

    if ai_tags_hit and object_hit:
        ai_involved, ai_category = "yes", "hybrid"
    elif object_hit:
        ai_involved, ai_category = "yes", "object"
    elif ai_tags_hit:
        ai_involved, ai_category = "yes", "tool"
    elif general_ai and (
        "AI" in p.get("title", "") or "artificial intelligence" in p.get("title", "").lower()
    ):
        # 标题含 AI 但方法不是 AI 工具 → 可能把 AI 作为研究对象
        ai_involved, ai_category = "yes", "object"
    else:
        ai_involved, ai_category = "no", "n/a"

    ai_subcategory = "n/a"
    if ai_involved == "yes":
        if ai_category == "tool" and ai_tags_hit:
            ai_subcategory = AI_TOOL_SUBCAT.get(ai_tags_hit[0], "other")
        elif ai_category == "object":
            # 根据命中哪条 object 规则大致归类
            if re.search(r"\baudit\b", text, re.I):
                ai_subcategory = "algorithmic_audit"
            elif re.search(r"\b(bias|discriminat|fairness)\b", text, re.I):
                ai_subcategory = "ai_bias_fairness"
            elif re.search(r"\b(ghost work|data (?:labeler|annotator)|moderator)\b", text, re.I):
                ai_subcategory = "ai_labor_infrastructure"
            elif re.search(r"\b(governance|regulation|policy)\b", text, re.I):
                ai_subcategory = "ai_governance"
            elif re.search(r"\b(perceive|experience|interact with|resist)\b", text, re.I):
                ai_subcategory = "human_ai_interaction_study"
            else:
                ai_subcategory = "ai_object_other"
        elif ai_category == "hybrid":
            ai_subcategory = "hybrid_tool_object"

    # methodological_innovation 判定：方法刊 or 匹配 methodological/theoretical 标签
    methodological_innovation = "no"
    if l1_primary == "methodological":
        methodological_innovation = "yes"

    # teaching_candidate 粗判定：AI 相关 or 方法创新。硬上限在 generate_outputs 中处理。
    teaching_candidate = "no"  # 启发式保守，深度编码阶段再补

    evidence_notes = "; ".join(f"{t}←“{ev}”" for t, ev in uniq[:3])

    return {
        "openalex_id": p["openalex_id"],
        "l1_primary": l1_primary,
        "l1_secondary": l1_secondary,
        "data_type": "?",
        "data_source": "?",
        "sample_size": "?",
        "time_window_data": "?",
        "geographic_scope": "?",
        "analytic_tools": "?",
        "validity_strategy": "?",
        "ai_involved": ai_involved,
        "ai_category": ai_category,
        "ai_subcategory": ai_subcategory,
        "ai_role": "" if ai_involved == "no" else f"auto-detected via rules; see notes",
        "ai_model_used": "" if ai_involved == "no" else (
            "LLM-family" if "ai.llm" in {t for t, _ in uniq} else
            "CV model" if "ai.cv" in {t for t, _ in uniq} else
            "ML classifier" if "ai.ml_supervised" in {t for t, _ in uniq} else
            "unspecified"
        ),
        "validation_of_ai": "",
        "ethics_statement": "",
        "teaching_hook": "",
        "methodological_innovation": methodological_innovation,
        "teaching_candidate": teaching_candidate,
        "l3_operational_summary": "",
        "notes": f"[heuristic] {evidence_notes}" if evidence_notes else "[heuristic] no method keyword matched",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--papers", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    payload = json.loads(Path(args.papers).read_text(encoding="utf-8"))
    papers = payload["papers"]
    print(f"编码 {len(papers)} 篇论文...")

    classifications = [classify_one(p) for p in papers]

    # 统计
    from collections import Counter
    l1 = Counter(c["l1_primary"] for c in classifications)
    ai_cat = Counter(c["ai_category"] for c in classifications)
    no_match = sum(1 for c in classifications if c["l1_primary"] == "?")

    print(f"  L1 分布 (top 15)：")
    for t, n in l1.most_common(15):
        print(f"    {t:35s} {n:5d}")
    print(f"  AI 分布：")
    for t, n in ai_cat.most_common():
        print(f"    {t:15s} {n:5d}")
    print(f"  未匹配方法 (l1='?')：{no_match} 篇 ({no_match/len(papers)*100:.1f}%)")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"classifications": classifications}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✓ 保存：{out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
