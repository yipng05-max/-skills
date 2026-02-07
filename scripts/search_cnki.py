#!/usr/bin/env python3
"""
CNKI/Chinese Literature Search Script - Search Chinese academic databases via web queries.

Usage:
    python search_cnki.py --title "基于深度学习的文本分类研究"
    python search_cnki.py --title "文本分类" --author "张三"
    python search_cnki.py --query "深度学习 自然语言处理"

Output: JSON with constructed search URLs for CNKI, Wanfang, and CQVIP,
        plus CrossRef results if available.
"""

import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import argparse


def build_cnki_search_url(title=None, author=None):
    """Build CNKI search URL."""
    base = "https://kns.cnki.net/kns8s/search"
    params = {}
    if title:
        params["q"] = title
    if author:
        params["q"] = (params.get("q", "") + " " + author).strip()
    return f"{base}?{urllib.parse.urlencode(params)}" if params else base


def build_wanfang_search_url(title=None, author=None):
    """Build Wanfang search URL."""
    base = "https://s.wanfangdata.com.cn/paper"
    query = ""
    if title:
        query = title
    if author:
        query = (query + " " + author).strip()
    params = {"q": query} if query else {}
    return f"{base}?{urllib.parse.urlencode(params)}" if params else base


def build_cqvip_search_url(title=None, author=None):
    """Build CQVIP (维普) search URL."""
    base = "https://qikan.cqvip.com/Qikan/Search/Index"
    query = ""
    if title:
        query = title
    if author:
        query = (query + " " + author).strip()
    params = {"keyword": query} if query else {}
    return f"{base}?{urllib.parse.urlencode(params)}" if params else base


def search_crossref_chinese(title=None, author=None, rows=5):
    """Search CrossRef (may cover some Chinese journals with DOIs)."""
    params = {"rows": str(rows)}
    if title:
        params["query.title"] = title
    if author:
        params["query.author"] = author
    if not title and not author:
        return {"found": 0, "results": [], "note": "No search parameters"}

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
                published = (item.get("published-print")
                             or item.get("published-online")
                             or item.get("created"))
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
                    "score": item.get("score"),
                })
            return {"found": len(results), "results": results}
    except Exception as e:
        return {"found": 0, "error": str(e), "results": []}


def search_chinese_literature(title=None, author=None, query=None):
    """Generate search URLs and attempt CrossRef lookup for Chinese literature."""
    search_title = title or query
    result = {
        "search_urls": {
            "cnki": build_cnki_search_url(search_title, author),
            "wanfang": build_wanfang_search_url(search_title, author),
            "cqvip": build_cqvip_search_url(search_title, author),
            "google_scholar": (
                f"https://scholar.google.com/scholar?"
                f"{urllib.parse.urlencode({'q': (search_title or '') + ' ' + (author or '').strip()})}"
            ),
            "baidu_xueshu": (
                f"https://xueshu.baidu.com/s?"
                f"{urllib.parse.urlencode({'wd': (search_title or '') + ' ' + (author or '').strip()})}"
            ),
        },
        "crossref": search_crossref_chinese(title=search_title, author=author),
        "instructions": (
            "Chinese literature databases (CNKI, Wanfang, CQVIP) do not provide public APIs. "
            "Use the search URLs above with WebFetch or WebSearch to verify. "
            "Also try: WebSearch with query '<title> site:cnki.net' or '<title> site:wanfangdata.com.cn'"
        ),
    }
    return result


def main():
    parser = argparse.ArgumentParser(description="Search Chinese academic databases")
    parser.add_argument("--title", help="Search by title (Chinese or English)")
    parser.add_argument("--author", help="Search by author name")
    parser.add_argument("--query", help="Free-text search query")
    args = parser.parse_args()

    if not any([args.title, args.author, args.query]):
        parser.error("At least one of --title, --author, or --query is required")

    result = search_chinese_literature(
        title=args.title, author=args.author, query=args.query
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
