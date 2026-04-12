"""
V2EX 抓取器 - 中国程序员社区
"""
import httpx

V2EX_HOT_URL = "https://www.v2ex.com/api/topics/hot.json"
V2EX_LATEST_URL = "https://www.v2ex.com/api/topics/latest.json"


async def fetch_v2ex(top_n: int = 10) -> list[dict]:
    """抓取 V2EX 热门帖子"""
    items = []
    async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "DailyDigestBot/1.0"}) as client:
        try:
            resp = await client.get(V2EX_HOT_URL)
            topics = resp.json()

            for topic in topics[:top_n]:
                items.append({
                    "title": topic.get("title", ""),
                    "url": f"https://www.v2ex.com/t/{topic.get('id', '')}",
                    "author": topic.get("member", {}).get("username", ""),
                    "node": topic.get("node", {}).get("title", ""),
                    "replies": topic.get("replies", 0),
                    "source": "V2EX",
                    "created": topic.get("created", 0),
                })
        except Exception as e:
            print(f"V2EX fetch error: {e}")

    return items


if __name__ == "__main__":
    import asyncio
    results = asyncio.run(fetch_v2ex())
    for item in results:
        print(f"[{item['replies']}💬] {item['title'][:60]}")
