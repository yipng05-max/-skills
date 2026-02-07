---
name: literature-verifier
description: Verify the authenticity of literature references and detect hallucinations. Use when users need to check if a citation is real, verify a DOI, confirm a paper/article/book exists, cross-check author-title-journal-year metadata, detect fabricated references, validate URLs of online articles, or audit a reference list for accuracy. Covers journal papers, conference papers, preprints, books, monographs, newspaper articles, magazine articles, web articles, and any other published works.
---

# Literature Verifier

Verify authenticity and detect hallucinations in literature references of any type: journal articles, books, web articles, conference papers, preprints, newspaper/magazine articles, and more.

## Verification Workflow

1. **Parse** the reference to extract structured fields (title, authors, year, journal/venue, DOI, URL, ISBN)
2. **Verify existence** using available identifiers (DOI → CrossRef; URL → HTTP check; title → CrossRef search)
3. **Cross-check metadata** between claimed and actual values
4. **Assess confidence** and report findings
5. **Verify claims** if the user asks about specific content attributed to the source

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

## Hallucination Detection

When verification fails or metadata doesn't match, consult `references/hallucination-patterns.md` to identify which hallucination pattern applies. Common red flags:

- DOI doesn't resolve → likely fabricated DOI
- Title search returns no results → likely fabricated title
- Authors don't match → author hallucination
- Journal doesn't exist → venue hallucination
- Year is off → date hallucination

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
| **Uncertain** | No DOI, no exact title match, but components are plausible |
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
- **`scripts/verify_url.py`** — Check URL reachability and extract page metadata (title, author, DOI from meta tags).
- **`references/hallucination-patterns.md`** — Catalog of common hallucination types. Read when fabrication is suspected to classify the pattern.
- **`references/verification-checklist.md`** — Comprehensive step-by-step checklist. Read for thorough audits or when unsure what to check next.
