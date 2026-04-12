"""
Hacker News 抓取器 - 使用官方 API
"""
import httpx
import asyncio
from datetime import datetime, timezone

HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


async def fetch_hackernews(top_n: int = 20) -> list[dict]:
    """抓取 Hacker News Top Stories"""
    async with httpx.AsyncClient(timeout=30) as client:
        # 获取 top story IDs
        resp = await client.get(HN_TOP_URL)
        story_ids = resp.json()[:top_n]

        # 并发获取每个 story 详情
        tasks = [client.get(HN_ITEM_URL.format(sid)) for sid in story_ids]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        items = []
        for resp in responses:
            if isinstance(resp, Exception):
                continue
            try:
                data = resp.json()
                if not data or data.get("type") != "story":
                    continue
                items.append({
                    "title": data.get("title", ""),
                    "url": data.get("url", f"https://news.ycombinator.com/item?id={data['id']}"),
                    "score": data.get("score", 0),
                    "comments": data.get("descendants", 0),
                    "author": data.get("by", ""),
                    "source": "Hacker News",
                    "hn_url": f"https://news.ycombinator.com/item?id={data['id']}",
                    "time": datetime.fromtimestamp(data.get("time", 0), tz=timezone.utc).isoformat(),
                })
            except Exception:
                continue

        return items


if __name__ == "__main__":
    results = asyncio.run(fetch_hackernews())
    for item in results:
        print(f"[{item['score']}↑] {item['title']}")
