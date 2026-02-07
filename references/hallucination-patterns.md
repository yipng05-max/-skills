# Common Literature Hallucination Patterns

## DOI Hallucinations

1. **Fabricated DOI prefix**: DOI uses a registrant code that doesn't belong to the claimed publisher (e.g., a Springer DOI prefix on an Elsevier journal).
2. **Plausible but nonexistent DOI**: The DOI follows correct formatting (10.xxxx/xxxxx) but resolves to nothing.
3. **DOI mismatch**: The DOI is real but points to a completely different paper than described.

## Author Hallucinations

1. **Real author, wrong paper**: The author exists and publishes in the claimed field, but did not write the cited paper.
2. **Composite authors**: The name blends two real researchers (e.g., first name from one, last name from another).
3. **Plausible but nonexistent author**: The name sounds typical for the field but no such researcher exists.
4. **Incorrect author count or order**: Real paper exists but author list is wrong.

## Journal / Venue Hallucinations

1. **Nonexistent journal**: Journal name sounds plausible but does not exist (e.g., "Journal of Advanced Computational Neuroscience").
2. **Confused journal**: Mixes names of two real journals (e.g., "Nature Computational Biology" conflating Nature and PLoS Computational Biology).
3. **Wrong publisher**: Journal exists but is attributed to the wrong publisher.
4. **Incorrect ISSN**: ISSN doesn't match the journal or doesn't exist.

## Title Hallucinations

1. **Plausible but fabricated title**: The title uses domain-appropriate keywords but the paper doesn't exist.
2. **Paraphrased real title**: A real paper's title is slightly altered, making it unfindable.
3. **Title-content mismatch**: The title is from one paper but the described content is from another.

## Date / Volume / Page Hallucinations

1. **Impossible date**: Publication date is in the future or before the journal existed.
2. **Wrong year**: Paper exists but was published in a different year.
3. **Fabricated volume/issue/pages**: The paper exists but volume, issue, or page numbers are incorrect.

## Content / Claim Hallucinations

1. **Attributed claim fabrication**: A real paper exists but the specific finding or claim attributed to it does not appear in the paper.
2. **Statistical fabrication**: Specific numbers, p-values, or effect sizes are fabricated.
3. **Methodology misattribution**: The paper is real but used a different methodology than described.
4. **Conclusion reversal**: The paper's conclusion is stated as the opposite of what it actually found.

## URL / Link Hallucinations

1. **Fabricated URL**: URL follows a plausible pattern for the publisher but returns 404.
2. **Domain mismatch**: URL domain doesn't match the claimed publisher.
3. **Outdated URL**: URL once worked but the resource has moved or been removed.

## Retraction and Integrity Issues

1. **Citing retracted papers**: The paper exists but has been retracted.
2. **Citing predatory journals**: The journal exists but is a known predatory publisher.
3. **Preprint cited as published**: A preprint is cited as if it were peer-reviewed and published.
