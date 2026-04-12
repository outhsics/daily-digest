"""
Dev.to 抓取器 - 使用公开 API
"""
import httpx

DEVTO_TOP_URL = "https://dev.to/api/articles?top=1&per_page={}"
DEVTO_LATEST_URL = "https://dev.to/api/articles?per_page={}&state=rising"


async def fetch_devto(top_n: int = 10) -> list[dict]:
    """抓取 Dev.to 热门文章"""
    items = []
    seen = set()
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # Top articles today
            resp = await client.get(DEVTO_TOP_URL.format(top_n))
            articles = resp.json()

            for article in articles:
                aid = article.get("id")
                if aid in seen:
                    continue
                seen.add(aid)

                items.append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "description": article.get("description", "")[:300],
                    "author": article.get("user", {}).get("name", ""),
                    "reactions": article.get("public_reactions_count", 0),
                    "comments": article.get("comments_count", 0),
                    "tags": article.get("tag_list", []),
                    "reading_time": article.get("reading_time_minutes", 0),
                    "source": "Dev.to",
                    "published": article.get("published_at", ""),
                })
        except Exception as e:
            print(f"Dev.to fetch error: {e}")

    return items[:top_n]


if __name__ == "__main__":
    import asyncio
    results = asyncio.run(fetch_devto())
    for item in results:
        print(f"[{item['reactions']}❤] {item['title'][:60]}")
