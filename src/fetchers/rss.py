"""
RSS 订阅源抓取器
"""
import httpx
import feedparser
import asyncio
from datetime import datetime


async def fetch_rss(feed_url: str, source_name: str, top_n: int = 10) -> list[dict]:
    """抓取单个 RSS 源"""
    items = []
    async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as client:
        try:
            resp = await client.get(feed_url)
            feed = feedparser.parse(resp.text)

            for entry in feed.entries[:top_n]:
                # 提取摘要
                summary = ""
                if hasattr(entry, "summary"):
                    summary = entry.summary
                elif hasattr(entry, "description"):
                    summary = entry.description
                # 清理 HTML 标签（简单处理）
                summary = _clean_html(summary)[:500]

                published = ""
                if hasattr(entry, "published"):
                    published = entry.published
                elif hasattr(entry, "updated"):
                    published = entry.updated

                items.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": summary,
                    "author": entry.get("author", ""),
                    "published": published,
                    "source": source_name,
                })
        except Exception as e:
            print(f"RSS fetch error for {source_name}: {e}")

    return items


async def fetch_all_rss(feeds: dict, top_n: int = 10) -> list[dict]:
    """并发抓取所有 RSS 源"""
    tasks = [
        fetch_rss(url, name, top_n)
        for name, url in feeds.items()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items = []
    for result in results:
        if isinstance(result, list):
            all_items.extend(result)

    return all_items


def _clean_html(text: str) -> str:
    """简单清理 HTML 标签"""
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


if __name__ == "__main__":
    from src.config import RSS_FEEDS
    results = asyncio.run(fetch_all_rss(RSS_FEEDS))
    for item in results[:20]:
        print(f"[{item['source']}] {item['title'][:60]}")
