#!/usr/bin/env python3
"""
DOI Verification Script - Queries CrossRef and DOI.org APIs to verify DOI existence and metadata.

Usage:
    python verify_doi.py <doi>
    python verify_doi.py "10.1038/nature12373"

Output: JSON with verification status, metadata (title, authors, journal, year, type), and any discrepancies.
"""

import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import re


def normalize_doi(doi_input):
    """Extract and normalize a DOI from various input formats."""
    doi_input = doi_input.strip()
    patterns = [
        r'(10\.\d{4,9}/[^\s]+)',
        r'doi\.org/(10\.\d{4,9}/[^\s]+)',
        r'doi:\s*(10\.\d{4,9}/[^\s]+)',
    ]
    for p in patterns:
        m = re.search(p, doi_input, re.IGNORECASE)
        if m:
            return m.group(1).rstrip('.,;:)')
    return None


def query_crossref(doi):
    """Query CrossRef API for DOI metadata."""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "LiteratureVerifier/1.0 (mailto:verify@example.com)",
        "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            msg = data.get("message", {})
            title_list = msg.get("title", [])
            authors = []
            for a in msg.get("author", []):
                name_parts = []
                if a.get("given"):
                    name_parts.append(a["given"])
                if a.get("family"):
                    name_parts.append(a["family"])
                if name_parts:
                    authors.append(" ".join(name_parts))
            container = msg.get("container-title", [])
            published = msg.get("published-print") or msg.get("published-online") or msg.get("created")
            year = None
            if published and "date-parts" in published:
                parts = published["date-parts"]
                if parts and parts[0]:
                    year = parts[0][0]
            return {
                "found": True,
                "source": "crossref",
                "title": title_list[0] if title_list else None,
                "authors": authors,
                "journal": container[0] if container else None,
                "year": year,
                "type": msg.get("type"),
                "issn": msg.get("ISSN", []),
                "publisher": msg.get("publisher"),
                "url": msg.get("URL"),
                "reference_count": msg.get("reference-count"),
                "is_referenced_by_count": msg.get("is-referenced-by-count"),
            }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"found": False, "source": "crossref", "error": "DOI not found in CrossRef"}
        return {"found": False, "source": "crossref", "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"found": False, "source": "crossref", "error": str(e)}


def query_doi_org(doi):
    """Query DOI.org content negotiation for metadata."""
    url = f"https://doi.org/{urllib.parse.quote(doi, safe='')}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.citationstyles.csl+json",
        "User-Agent": "LiteratureVerifier/1.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            authors = []
            for a in data.get("author", []):
                name_parts = []
                if a.get("given"):
                    name_parts.append(a["given"])
                if a.get("family"):
                    name_parts.append(a["family"])
                if name_parts:
                    authors.append(" ".join(name_parts))
            issued = data.get("issued", {})
            year = None
            if "date-parts" in issued and issued["date-parts"] and issued["date-parts"][0]:
                year = issued["date-parts"][0][0]
            return {
                "found": True,
                "source": "doi.org",
                "title": data.get("title"),
                "authors": authors,
                "journal": data.get("container-title"),
                "year": year,
                "type": data.get("type"),
                "publisher": data.get("publisher"),
                "url": data.get("URL"),
            }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"found": False, "source": "doi.org", "error": "DOI not resolved"}
        return {"found": False, "source": "doi.org", "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"found": False, "source": "doi.org", "error": str(e)}


def verify_doi(doi_input):
    """Full DOI verification pipeline."""
    doi = normalize_doi(doi_input)
    if not doi:
        return {"verified": False, "error": "Could not extract a valid DOI from input", "raw_input": doi_input}

    result = {"doi": doi, "raw_input": doi_input}
    crossref = query_crossref(doi)
    doi_org = query_doi_org(doi)

    result["crossref"] = crossref
    result["doi_org"] = doi_org

    if crossref["found"] and doi_org["found"]:
        result["verified"] = True
        result["confidence"] = "high"
        result["metadata"] = {
            "title": crossref.get("title") or doi_org.get("title"),
            "authors": crossref.get("authors") or doi_org.get("authors"),
            "journal": crossref.get("journal") or doi_org.get("journal"),
            "year": crossref.get("year") or doi_org.get("year"),
            "type": crossref.get("type") or doi_org.get("type"),
            "publisher": crossref.get("publisher") or doi_org.get("publisher"),
            "citation_count": crossref.get("is_referenced_by_count"),
        }
    elif crossref["found"] or doi_org["found"]:
        source = crossref if crossref["found"] else doi_org
        result["verified"] = True
        result["confidence"] = "medium"
        result["metadata"] = {
            "title": source.get("title"),
            "authors": source.get("authors"),
            "journal": source.get("journal"),
            "year": source.get("year"),
            "type": source.get("type"),
            "publisher": source.get("publisher"),
        }
    else:
        result["verified"] = False
        result["confidence"] = "none"
        result["metadata"] = None

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_doi.py <doi>")
        print('Example: python verify_doi.py "10.1038/nature12373"')
        sys.exit(1)

    doi_input = " ".join(sys.argv[1:])
    result = verify_doi(doi_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("verified"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
