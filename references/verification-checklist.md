# Literature Verification Checklist

## Tier 1: Existence Verification (Must Do)

- [ ] **DOI check**: If DOI provided, run `verify_doi.py` to confirm it resolves
- [ ] **Title search**: Search CrossRef via `search_crossref.py --title "<title>"` to find matching works
- [ ] **Author-title match**: Verify the claimed authors match the actual paper authors
- [ ] **Publication venue**: Confirm the journal/conference/publisher exists and matches

## Tier 2: Metadata Accuracy (Should Do)

- [ ] **Year verification**: Confirm publication year matches the actual record
- [ ] **Volume / issue / pages**: Cross-check against CrossRef or publisher metadata
- [ ] **Author order and completeness**: Verify full author list and order
- [ ] **Publisher**: Confirm the publisher matches (e.g., Springer vs Elsevier)
- [ ] **ISSN check**: If provided, verify ISSN matches the journal

## Tier 3: Content Verification (When Claims Are Cited)

- [ ] **Access the full text**: Attempt to retrieve the paper (via DOI link, publisher URL, or web search)
- [ ] **Claim verification**: Check that the specific claim attributed to the paper actually appears in it
- [ ] **Methodology check**: Verify the described methodology matches the paper
- [ ] **Statistical verification**: Confirm cited statistics, p-values, effect sizes

## Tier 4: Integrity Assessment (When Relevant)

- [ ] **Retraction check**: Search Retraction Watch or publisher notices
- [ ] **Journal quality**: Check if the journal is indexed in major databases (Scopus, Web of Science)
- [ ] **Preprint status**: Determine if the work is a preprint vs. peer-reviewed publication
- [ ] **Predatory publisher check**: Verify the publisher is not on known predatory publisher lists

## Verification Confidence Levels

| Level | Meaning | Criteria |
|-------|---------|----------|
| **Confirmed** | Literature verified as authentic | DOI resolves, metadata matches across sources, full text accessible |
| **Likely Real** | Strong evidence of authenticity | DOI resolves OR title+author match found, minor metadata discrepancies |
| **Uncertain** | Cannot confirm or deny | No DOI, title search yields no exact match, but components are plausible |
| **Likely Fabricated** | Strong evidence of hallucination | DOI doesn't resolve, no matching work found, hallucination patterns detected |
| **Confirmed Fabricated** | Definitely hallucinated | Multiple indicators of fabrication, no trace of the work in any database |

## Web Article Verification

- [ ] **URL reachability**: Run `verify_url.py` to check if the URL is live
- [ ] **Archive check**: Search Wayback Machine if URL is dead (`web.archive.org/web/<url>`)
- [ ] **Author verification**: Search for the author on the publication's website
- [ ] **Date verification**: Check page metadata and Wayback Machine for original publication date
- [ ] **Content cross-reference**: Search key claims on other reputable sources

## Book / Monograph Verification

- [ ] **ISBN check**: Verify ISBN via Open Library API or WorldCat
- [ ] **Publisher verification**: Confirm the publisher exists and has published the claimed work
- [ ] **Author bibliography**: Check the author's known bibliography for the claimed work
- [ ] **Library catalog search**: Search WorldCat (worldcat.org) for the book record
