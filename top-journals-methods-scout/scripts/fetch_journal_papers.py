#!/usr/bin/env python3
"""
按 ISSN 批量抓取 OpenAlex 上各期刊近 N 个月的论文元数据。

用法：
    python3 fetch_journal_papers.py \
        --journals-file /path/to/journals.json \
        --months 24 \
        --disciplines sociology political_science ai_social_intersection \
        --out /tmp/methods_scout/papers.json

若 --disciplines 省略，则抓取 journals.json 中全部学科。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

OPENALEX_API = "https://api.openalex.org/works"
PER_PAGE = 200
SLEEP_BETWEEN = 0.15  # 礼貌间隔，OpenAlex 建议 <=10 req/s
MAILTO = "polite@example.org"  # OpenAlex polite pool


def iso_months_ago(months: int) -> str:
    today = date.today()
    days = int(months * 30.44)
    return (today - timedelta(days=days)).isoformat()


def fetch_for_issn(issn_list: list[str], since: str) -> list[dict]:
    """按 ISSN 集合拉取所有论文（cursor 翻页）。"""
    issn_filter = "|".join(issn_list)
    cursor = "*"
    rows: list[dict] = []
    while True:
        params = (
            f"filter=primary_location.source.issn:{quote(issn_filter)},"
            f"from_publication_date:{since},"
            f"type:article"
            f"&per-page={PER_PAGE}"
            f"&cursor={cursor}"
            f"&mailto={MAILTO}"
            f"&select=id,doi,title,display_name,publication_date,publication_year,"
            f"authorships,primary_location,abstract_inverted_index,keywords,"
            f"cited_by_count,concepts,topics"
        )
        url = f"{OPENALEX_API}?{params}"
        req = Request(url, headers={"User-Agent": "top-journals-methods-scout/1.0"})
        try:
            with urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
        except (HTTPError, URLError) as e:
            print(f"  ! 请求失败 ({e}); ISSN={issn_list}", file=sys.stderr)
            return rows
        results = data.get("results", [])
        rows.extend(results)
        next_cursor = data.get("meta", {}).get("next_cursor")
        if not next_cursor or not results:
            break
        cursor = next_cursor
        time.sleep(SLEEP_BETWEEN)
    return rows


def reconstruct_abstract(inv_index: dict | None) -> str:
    if not inv_index:
        return ""
    pos2word: dict[int, str] = {}
    for word, positions in inv_index.items():
        for p in positions:
            pos2word[p] = word
    return " ".join(pos2word[i] for i in sorted(pos2word.keys()))


def flatten_paper(p: dict, journal_name: str, discipline: str) -> dict:
    authors = [
        a.get("author", {}).get("display_name", "")
        for a in p.get("authorships", [])
    ]
    return {
        "openalex_id": p.get("id", ""),
        "doi": p.get("doi", "") or "",
        "title": p.get("title") or p.get("display_name", ""),
        "authors": "; ".join([a for a in authors if a]),
        "publication_date": p.get("publication_date", ""),
        "publication_year": p.get("publication_year", ""),
        "journal": journal_name,
        "discipline": discipline,
        "abstract": reconstruct_abstract(p.get("abstract_inverted_index")),
        "keywords": "; ".join(
            [k.get("display_name", "") for k in (p.get("keywords") or [])]
        ),
        "concepts": "; ".join(
            [
                c.get("display_name", "")
                for c in (p.get("concepts") or [])[:10]
            ]
        ),
        "topics": "; ".join(
            [
                t.get("display_name", "")
                for t in (p.get("topics") or [])[:5]
            ]
        ),
        "cited_by_count": p.get("cited_by_count", 0),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--journals-file", required=True)
    ap.add_argument("--months", type=int, default=24)
    ap.add_argument("--disciplines", nargs="*", default=None,
                    help="学科键名列表；省略则抓取全部")
    ap.add_argument("--out", required=True, help="输出 JSON 文件路径")
    args = ap.parse_args()

    with open(args.journals_file, "r", encoding="utf-8") as f:
        journals = json.load(f)

    all_disciplines = journals["disciplines"]
    target_disciplines = args.disciplines or list(all_disciplines.keys())
    since = iso_months_ago(args.months)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"检索窗口：{since} → 今天（近 {args.months} 个月）")
    print(f"目标学科：{', '.join(target_disciplines)}")
    print("-" * 60)

    all_rows: list[dict] = []
    summary: list[dict] = []

    for disc in target_disciplines:
        if disc not in all_disciplines:
            print(f"⚠ 未知学科键：{disc}，跳过")
            continue
        for j in all_disciplines[disc]:
            name = j["name"]
            issns = j["issn"]
            print(f"[{disc}] {name}  ISSN={issns}")
            papers = fetch_for_issn(issns, since)
            for p in papers:
                all_rows.append(flatten_paper(p, name, disc))
            print(f"    → {len(papers)} 篇")
            summary.append({"discipline": disc, "journal": name, "count": len(papers)})
            time.sleep(SLEEP_BETWEEN)

    # 去重（按 DOI 或 OpenAlex id）
    seen = set()
    deduped: list[dict] = []
    for row in all_rows:
        key = row["doi"] or row["openalex_id"]
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    payload = {
        "meta": {
            "since": since,
            "months": args.months,
            "disciplines": target_disciplines,
            "total_raw": len(all_rows),
            "total_deduped": len(deduped),
            "per_journal": summary,
        },
        "papers": deduped,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("-" * 60)
    print(f"✓ 总计 {len(deduped)} 篇（去重后）保存至 {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
