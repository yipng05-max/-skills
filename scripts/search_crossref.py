#!/usr/bin/env python3
"""
CrossRef Search Script - Search for literature by title, author, or keywords.

Usage:
    python search_crossref.py --title "Attention Is All You Need"
    python search_crossref.py --title "some title" --author "Smith"
    python search_crossref.py --query "transformer neural network"

Output: JSON list of matching works with metadata.
"""

import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import argparse


def search_crossref(title=None, author=None, query=None, rows=5):
    """Search CrossRef for works matching the given criteria."""
    params = {"rows": str(rows)}

    if query:
        params["query"] = query
    if title:
        params["query.title"] = title
    if author:
        params["query.author"] = author

    url = f"https://api.crossref.org/works?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "LiteratureVerifier/1.0 (mailto:verify@example.com)",
        "Accept": "application/json"
    })

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            items = data.get("message", {}).get("items", [])
            results = []
            for item in items:
                title_list = item.get("title", [])
                authors = []
                for a in item.get("author", []):
                    parts = []
                    if a.get("given"):
                        parts.append(a["given"])
                    if a.get("family"):
                        parts.append(a["family"])
                    if parts:
                        authors.append(" ".join(parts))

                container = item.get("container-title", [])
                published = item.get("published-print") or item.get("published-online") or item.get("created")
                year = None
                if published and "date-parts" in published:
                    dp = published["date-parts"]
                    if dp and dp[0]:
                        year = dp[0][0]

                results.append({
                    "title": title_list[0] if title_list else None,
                    "authors": authors,
                    "journal": container[0] if container else None,
                    "year": year,
                    "doi": item.get("DOI"),
                    "type": item.get("type"),
                    "publisher": item.get("publisher"),
                    "url": item.get("URL"),
                    "score": item.get("score"),
                    "citation_count": item.get("is-referenced-by-count"),
                })

            return {"found": len(results), "results": results}
    except urllib.error.HTTPError as e:
        return {"found": 0, "error": f"HTTP {e.code}: {e.reason}", "results": []}
    except Exception as e:
        return {"found": 0, "error": str(e), "results": []}


def main():
    parser = argparse.ArgumentParser(description="Search CrossRef for literature")
    parser.add_argument("--title", help="Search by title")
    parser.add_argument("--author", help="Search by author name")
    parser.add_argument("--query", help="Free-text search query")
    parser.add_argument("--rows", type=int, default=5, help="Max results (default: 5)")
    args = parser.parse_args()

    if not any([args.title, args.author, args.query]):
        parser.error("At least one of --title, --author, or --query is required")

    result = search_crossref(title=args.title, author=args.author, query=args.query, rows=args.rows)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
