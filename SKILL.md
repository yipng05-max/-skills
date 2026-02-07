---
name: literature-verifier
description: Verify the authenticity of literature references and detect hallucinations in both English and Chinese (中文) sources. Use when users need to check if a citation is real, verify a DOI, confirm a paper/article/book exists, cross-check author-title-journal-year metadata, detect fabricated references, validate URLs of online articles, or audit a reference list for accuracy. Covers journal papers, conference papers, preprints, books, monographs, newspaper articles, magazine articles, web articles, dissertations, government documents, and any other published works. Supports Chinese academic databases including CNKI (知网), Wanfang (万方), CQVIP (维普), Baidu Scholar (百度学术), and core journal list verification (北大核心, CSSCI, CSCD).
---

# Literature Verifier

Verify authenticity and detect hallucinations in literature references of any type and any language: journal articles, books, web articles, conference papers, preprints, newspaper/magazine articles, dissertations, government documents, and more. Full support for both English and Chinese (中文) literature verification.

## Verification Workflow

1. **Detect language**: Determine if the reference is Chinese or English (or mixed)
2. **Parse** the reference to extract structured fields (title, authors, year, journal/venue, DOI, URL, ISBN)
3. **Verify existence** using appropriate sources:
   - English: DOI → CrossRef; URL → HTTP check; title → CrossRef search
   - Chinese: title → CNKI/Wanfang/CQVIP via WebSearch; DOI → CrossRef (if available)
4. **Cross-check metadata** between claimed and actual values
5. **Assess confidence** and report findings
6. **Verify claims** if the user asks about specific content attributed to the source

## Verification by Identifier Type

### Has DOI

Run `scripts/verify_doi.py "<doi>"`. Compare returned metadata (title, authors, journal, year) against the user's citation. Flag any mismatch.

### Has Title (No DOI)

Run `scripts/search_crossref.py --title "<title>"`. If results return, compare the top match's metadata against the citation. If no match, try adding `--author "<last_name>"`.

### Has URL

Run `scripts/verify_url.py "<url>"`. Check reachability, page title, and extracted metadata (citation_doi, citation_title, article_author). If URL is dead, suggest Wayback Machine: `web.archive.org/web/<url>`.

### Has ISBN (Books)

Use WebSearch to query `"ISBN <number>" site:openlibrary.org OR site:worldcat.org` and verify the book record.

### Minimal Information

Use WebSearch to search for the claimed title + author + year. Cross-reference results from Google Scholar (`site:scholar.google.com`), publisher sites, and library catalogs.

## Chinese Literature Verification (中文文献核查)

Chinese literature requires different verification strategies because most Chinese publications are not indexed in CrossRef. **You MUST use WebSearch as the primary verification tool** — do NOT merely generate search URLs or defer verification with "需知网核实". Every Chinese reference MUST receive a definitive verdict.

### MANDATORY Chinese Verification Procedure (必须执行)

For EVERY Chinese reference, execute ALL of the following WebSearch queries. Do NOT skip any step. Do NOT mark a paper as "Uncertain" without completing all searches.

#### Step 1: Multi-source WebSearch (必做 — 至少3次搜索)

Execute these WebSearch queries in sequence for each paper:

1. **Exact title search**: `"<完整论文标题>"` (with quotes, no site restriction)
2. **Title + author search**: `<论文标题> <作者姓名>` (without quotes, broader match)
3. **Title + journal search**: `<论文标题> <期刊名>` (cross-validate venue)
4. **CNKI-targeted search**: `"<论文标题>" site:cnki.net` (知网)
5. **Wanfang-targeted search**: `"<论文标题>" site:wanfangdata.com.cn` (万方)

If steps 1-3 already confirm the paper exists with matching metadata, steps 4-5 are supplementary. If steps 1-3 yield no results, steps 4-5 are MANDATORY.

#### Step 2: Metadata Cross-check (元数据交叉核验)

From the search results, verify:
- Author name matches
- Journal name matches exactly (beware 学报/杂志/期刊 confusion)
- Publication year matches
- Volume/issue/page numbers if available

#### Step 3: Verdict (必须给出明确判定)

Based on search results, assign ONE of these verdicts — **"Uncertain" is NOT acceptable as a final verdict for Chinese literature**:

| Verdict | Criteria |
|---------|----------|
| **Confirmed** | Found on 2+ sources (CNKI, Wanfang, Baidu Scholar, Google Scholar) with matching metadata |
| **Likely Real** | Found on 1 source with matching metadata, OR found with minor metadata discrepancies |
| **Likely Fabricated** | No results from any search, OR title/author/journal combination not found anywhere |
| **Confirmed Fabricated** | Multiple fabrication indicators: journal doesn't exist, author not in claimed institution, impossible date, etc. |
| **Metadata Error** | Paper exists but with different author/year/journal than claimed |

### Chinese Journal Articles (中文期刊论文)

1. **PRIMARY**: Execute the Multi-source WebSearch procedure above
2. **SUPPLEMENTARY**: Run `scripts/search_cnki.py --title "<中文标题>"` to attempt CrossRef lookup (some Chinese journals have DOIs)
3. If the reference has a DOI, also run `scripts/verify_doi.py` — but note that missing DOI does NOT indicate fabrication for Chinese literature

### Chinese Books / Monographs (中文图书/专著)

1. Use WebSearch to query `"<书名>" "<作者>" site:book.douban.com` (豆瓣读书)
2. Use WebSearch to query `"ISBN <号码>"` if ISBN is provided
3. Search National Library of China: `"<书名>" site:opac.nlc.cn`
4. Verify publisher exists and has published the claimed work

### Chinese Dissertations (学位论文)

1. Use WebSearch to query `"<论文标题>" 学位论文 site:cnki.net`
2. Use WebSearch to query `"<论文标题>" 学位论文 site:wanfangdata.com.cn`
3. Verify the degree-granting institution has the relevant discipline

### Chinese Government Documents (政策文件)

1. Use WebSearch to query `"<发文字号>" site:gov.cn`
2. Verify the issuing agency and document number format

### Chinese News Articles (新闻报道)

1. Use WebSearch to query on the claimed media's domain: `"<标题关键词>" site:<媒体域名>`
2. For People's Daily: `site:people.com.cn`; for Xinhua: `site:xinhuanet.com`

### Core Journal Verification (核心期刊验证)

When a reference claims the journal is a core journal (核心期刊), verify against:
- **北大核心**: 《中文核心期刊要目总览》— use WebSearch to check
- **CSSCI (南大核心)**: 中文社会科学引文索引来源期刊 — use WebSearch to check
- **CSCD**: 中国科学引文数据库来源期刊 — use WebSearch to check
- Note: Core journal status changes across editions; verify for the specific year claimed

### Key Differences for Chinese Literature

- **No DOI ≠ fabricated**: Most Chinese journal articles lack DOIs; absence of DOI is not evidence of fabrication
- **Author name formats**: Chinese names in English contexts may appear as "Zhang San", "San Zhang", or "S. Zhang"
- **Indexing lag**: Recently published papers may not yet appear in CNKI
- **Paywall**: CNKI/Wanfang require paid access for full text, but search results and abstracts are usually visible
- **NEVER defer verification**: Do NOT output "需知网核实" or "Uncertain (needs CNKI verification)" as a final result. Always use WebSearch to actually search and provide a definitive verdict.
- **WebSearch is your primary tool**: Chinese databases block automated scripts, so always use WebSearch (which accesses real search engines) instead of relying solely on Python scripts for Chinese literature

## Hallucination Detection

When verification fails or metadata doesn't match, consult `references/hallucination-patterns.md` (English) or `references/chinese-hallucination-patterns.md` (中文) to identify which hallucination pattern applies. Common red flags:

- DOI doesn't resolve → likely fabricated DOI (but NOT for Chinese literature without DOI)
- Title search returns no results → likely fabricated title
- Authors don't match → author hallucination
- Journal doesn't exist → venue hallucination
- Year is off → date hallucination
- Chinese journal claimed as core but not in official list → core journal hallucination
- CNKI + Wanfang + Baidu Scholar all return no results → strong indicator of fabrication for Chinese literature

## Batch Verification

When the user provides a reference list, verify each entry sequentially. Produce a summary table:

```
| # | Citation (short) | DOI verified | Title match | Author match | Year match | Confidence |
|---|-----------------|-------------|-------------|--------------|------------|------------|
| 1 | Smith 2020...   | Yes         | Yes         | Yes          | Yes        | Confirmed  |
| 2 | Jones 2019...   | No DOI      | No match    | -            | -          | Likely Fabricated |
```

## Confidence Levels

| Level | Criteria |
|-------|----------|
| **Confirmed** | DOI resolves AND metadata matches across sources |
| **Likely Real** | DOI resolves OR title+author match found, minor discrepancies |
| **Uncertain** | No DOI, no exact title match, but components are plausible. **For Chinese literature, this level is NOT acceptable as final verdict — must execute full WebSearch procedure first.** |
| **Likely Fabricated** | DOI doesn't resolve, no matching work found, hallucination patterns detected |
| **Confirmed Fabricated** | Multiple fabrication indicators, no trace in any database |

## Content Claim Verification

When the user asks whether a specific claim is actually stated in a source:

1. Retrieve the source (via DOI link, publisher URL, or web search)
2. Use WebFetch to read the page content if accessible
3. Search for the specific claim, statistic, or quote
4. Report whether the claim is supported, unsupported, or contradicted

## Report Format

For each verified reference, output:

```
**Reference**: [original citation text]
**Status**: [Confirmed / Likely Real / Uncertain / Likely Fabricated / Confirmed Fabricated]
**Findings**:
- DOI: [resolves / not found / not provided]
- Title: [exact match / partial match / no match]
- Authors: [match / mismatch / details]
- Journal/Venue: [verified / not found]
- Year: [correct / incorrect (actual: XXXX)]
**Issues**: [list any discrepancies or hallucination patterns detected]
**Actual Source** (if different): [correct metadata if the reference is a distortion of a real work]
```

## Resources

- **`scripts/verify_doi.py`** — Verify DOI existence via CrossRef and DOI.org APIs. Returns metadata for comparison.
- **`scripts/search_crossref.py`** — Search CrossRef by title/author/keywords. Find whether a claimed work exists.
- **`scripts/search_cnki.py`** — Generate search URLs for Chinese databases (CNKI, Wanfang, CQVIP, Baidu Scholar) and attempt CrossRef lookup. Supplementary tool — always use WebSearch as primary verification method for Chinese literature.
- **`scripts/verify_chinese.py`** — Attempt direct HTTP verification against Baidu Scholar, CNKI, and Wanfang. May be blocked by anti-bot measures — if so, fall back to WebSearch. Usage: `python scripts/verify_chinese.py --title "<中文标题>" --author "<作者>"`
- **`scripts/verify_url.py`** — Check URL reachability and extract page metadata (title, author, DOI from meta tags).
- **`references/hallucination-patterns.md`** — Catalog of common hallucination types for English literature. Read when fabrication is suspected.
- **`references/chinese-hallucination-patterns.md`** — Catalog of hallucination types specific to Chinese literature (中文文献幻觉模式). Read when Chinese reference fabrication is suspected.
- **`references/verification-checklist.md`** — Comprehensive step-by-step checklist for English literature verification.
- **`references/chinese-verification-checklist.md`** — Comprehensive checklist for Chinese literature verification (中文文献核验清单), including CNKI, Wanfang, core journal, dissertation, and government document checks.
