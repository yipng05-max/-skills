#!/usr/bin/env python3
"""
URL Verification Script - Check if a URL is reachable and extract metadata.

Usage:
    python verify_url.py <url>
    python verify_url.py "https://example.com/article"

Output: JSON with HTTP status, page title, meta description, and reachability.
"""

import sys
import json
import urllib.request
import urllib.error
import re
import ssl


def extract_meta(html, name):
    """Extract content from a meta tag."""
    patterns = [
        rf'<meta\s+name="{name}"\s+content="([^"]*)"',
        rf'<meta\s+content="([^"]*)"\s+name="{name}"',
        rf'<meta\s+property="{name}"\s+content="([^"]*)"',
        rf'<meta\s+content="([^"]*)"\s+property="{name}"',
    ]
    for p in patterns:
        m = re.search(p, html, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def verify_url(url):
    """Verify a URL is reachable and extract basic metadata."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = {"url": url}
    ctx = ssl.create_default_context()

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (LiteratureVerifier/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })

    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            result["status_code"] = resp.status
            result["reachable"] = True
            result["final_url"] = resp.url
            result["content_type"] = resp.headers.get("Content-Type", "")

            if "text/html" in result["content_type"]:
                html = resp.read(50000).decode("utf-8", errors="replace")
                title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
                result["page_title"] = title_match.group(1).strip() if title_match else None
                result["meta_description"] = extract_meta(html, "description")
                result["og_title"] = extract_meta(html, "og:title")
                result["og_type"] = extract_meta(html, "og:type")
                result["article_author"] = extract_meta(html, "author") or extract_meta(html, "article:author")
                result["article_published"] = extract_meta(html, "article:published_time") or extract_meta(html, "date")
                result["citation_doi"] = extract_meta(html, "citation_doi")
                result["citation_title"] = extract_meta(html, "citation_title")
                result["citation_journal"] = extract_meta(html, "citation_journal_title")
            elif "application/pdf" in result["content_type"]:
                result["page_title"] = None
                result["note"] = "URL points to a PDF file"

    except urllib.error.HTTPError as e:
        result["status_code"] = e.code
        result["reachable"] = False
        result["error"] = f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        result["reachable"] = False
        result["error"] = f"URL error: {e.reason}"
    except Exception as e:
        result["reachable"] = False
        result["error"] = str(e)

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_url.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    result = verify_url(url)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("reachable"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
