#!/usr/bin/env python3
"""
Chinese Literature Verification Script - Actually searches and verifies Chinese papers
using Baidu Scholar and other open sources.

Usage:
    python verify_chinese.py --title "论文标题" --author "作者" --journal "期刊名" --year 2020
    python verify_chinese.py --title "分配公平与程序公平对工作倦怠的影响"

Output: JSON with verification results from multiple sources.
"""

import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import re
import argparse
import ssl
import time


def search_baidu_xueshu(title, author=None, rows=5):
    """Search Baidu Scholar (百度学术) and parse results."""
    query = title
    if author:
        query = f"{title} {author}"
    url = f"https://xueshu.baidu.com/s?wd={urllib.parse.quote(query)}&rsv_bp=0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            results = []
            # Extract paper entries
            blocks = re.findall(r'<div class="sc_content"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
            if not blocks:
                blocks = re.findall(r'class="result[^"]*"[^>]*>(.*?)<div class="(?:result|page_footer)', html, re.DOTALL)

            # Try extracting titles and metadata
            titles = re.findall(r'<a[^>]*class="sc_q"[^>]*>(.*?)</a>', html, re.DOTALL)
            if not titles:
                titles = re.findall(r'<h3[^>]*><a[^>]*>(.*?)</a></h3>', html, re.DOTALL)

            # Extract citation counts
            cite_counts = re.findall(r'被引量[：:]\s*(\d+)', html)
            if not cite_counts:
                cite_counts = re.findall(r'被引[：:]?\s*<[^>]*>(\d+)', html)

            # Extract journal info
            journals = re.findall(r'<a[^>]*data-click[^>]*class="sc_q"[^>]*>([^<]+)</a>\s*,?\s*(\d{4})', html, re.DOTALL)

            for i, t in enumerate(titles[:rows]):
                clean_title = re.sub(r'<[^>]+>', '', t).strip()
                result = {"title": clean_title, "source": "baidu_xueshu"}
                if i < len(cite_counts):
                    result["citations"] = int(cite_counts[i])
                results.append(result)

            # Check if the exact title appears in the page
            clean_html = re.sub(r'<[^>]+>', '', html)
            clean_title_search = re.sub(r'\s+', '', title)
            clean_html_search = re.sub(r'\s+', '', clean_html)
            exact_match = clean_title_search in clean_html_search

            # Also check for partial matches
            title_keywords = [w for w in re.split(r'[，,：:、\s]+', title) if len(w) >= 2]
            keyword_matches = sum(1 for kw in title_keywords if kw in clean_html)
            keyword_ratio = keyword_matches / len(title_keywords) if title_keywords else 0

            return {
                "source": "baidu_xueshu",
                "url": url,
                "exact_title_found": exact_match,
                "keyword_match_ratio": round(keyword_ratio, 2),
                "results_count": len(titles),
                "results": results[:rows],
                "page_length": len(html),
            }
    except Exception as e:
        return {"source": "baidu_xueshu", "error": str(e), "url": url}


def search_cnki_web(title, author=None):
    """Search CNKI via web and check if results contain the paper."""
    query = title
    if author:
        query = f"{title} {author}"
    url = f"https://kns.cnki.net/kns8s/search?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            clean_html = re.sub(r'<[^>]+>', '', html)
            clean_html = re.sub(r'\s+', '', clean_html)
            clean_title = re.sub(r'\s+', '', title)
            found = clean_title in clean_html

            # Check for author if provided
            author_found = None
            if author:
                author_found = author in clean_html

            return {
                "source": "cnki",
                "url": url,
                "title_found_in_page": found,
                "author_found": author_found,
                "page_length": len(html),
            }
    except Exception as e:
        return {"source": "cnki", "error": str(e), "url": url}


def search_wanfang_web(title, author=None):
    """Search Wanfang via web."""
    query = title
    if author:
        query = f"{title} {author}"
    url = f"https://s.wanfangdata.com.cn/paper?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            clean_html = re.sub(r'<[^>]+>', '', html)
            clean_html = re.sub(r'\s+', '', clean_html)
            clean_title = re.sub(r'\s+', '', title)
            found = clean_title in clean_html
            return {
                "source": "wanfang",
                "url": url,
                "title_found_in_page": found,
                "page_length": len(html),
            }
    except Exception as e:
        return {"source": "wanfang", "error": str(e), "url": url}


def crossref_search(title, author=None, rows=3):
    """Search CrossRef (some Chinese journals have DOIs)."""
    params = {"rows": str(rows), "query.title": title}
    if author:
        params["query.author"] = author
    url = f"https://api.crossref.org/works?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "LiteratureVerifier/1.0 (mailto:verify@example.com)",
        "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            items = data.get("message", {}).get("items", [])
            results = []
            for item in items:
                t = item.get("title", [None])[0]
                results.append({
                    "title": t,
                    "doi": item.get("DOI"),
                    "journal": (item.get("container-title") or [None])[0],
                    "year": None,
                    "score": item.get("score"),
                })
            return {"source": "crossref", "found": len(results), "results": results}
    except Exception as e:
        return {"source": "crossref", "error": str(e)}


def verify_chinese_paper(title, author=None, journal=None, year=None):
    """Full verification pipeline for Chinese literature."""
    result = {
        "query": {"title": title, "author": author, "journal": journal, "year": year},
        "sources": {},
    }

    # 1. Baidu Scholar
    result["sources"]["baidu_xueshu"] = search_baidu_xueshu(title, author)
    time.sleep(0.5)

    # 2. CNKI
    result["sources"]["cnki"] = search_cnki_web(title, author)
    time.sleep(0.5)

    # 3. Wanfang
    result["sources"]["wanfang"] = search_wanfang_web(title, author)
    time.sleep(0.5)

    # 4. CrossRef
    result["sources"]["crossref"] = crossref_search(title, author)

    # Assess confidence
    baidu = result["sources"].get("baidu_xueshu", {})
    cnki = result["sources"].get("cnki", {})
    wanfang = result["sources"].get("wanfang", {})
    crossref = result["sources"].get("crossref", {})

    signals = []
    if baidu.get("exact_title_found"):
        signals.append("baidu_exact")
    elif baidu.get("keyword_match_ratio", 0) >= 0.7:
        signals.append("baidu_partial")
    if cnki.get("title_found_in_page"):
        signals.append("cnki_found")
    if wanfang.get("title_found_in_page"):
        signals.append("wanfang_found")
    if crossref.get("found", 0) > 0:
        top = crossref["results"][0] if crossref.get("results") else {}
        if top.get("score", 0) > 50:
            signals.append("crossref_high_score")

    if len(signals) >= 3:
        result["confidence"] = "high"
        result["verified"] = True
    elif len(signals) >= 2:
        result["confidence"] = "medium"
        result["verified"] = True
    elif len(signals) >= 1:
        result["confidence"] = "low"
        result["verified"] = True
    else:
        result["confidence"] = "none"
        result["verified"] = False

    result["signals"] = signals
    return result


def main():
    parser = argparse.ArgumentParser(description="Verify Chinese literature")
    parser.add_argument("--title", required=True, help="Paper title (Chinese)")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--journal", help="Journal name")
    parser.add_argument("--year", type=int, help="Publication year")
    args = parser.parse_args()

    result = verify_chinese_paper(
        title=args.title, author=args.author,
        journal=args.journal, year=args.year
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("verified"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
