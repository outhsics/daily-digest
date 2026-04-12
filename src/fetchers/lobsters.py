"""
Lobste.rs 抓取器 - 使用 JSON API
"""
import httpx

LOBSTERS_URL = "https://lobste.rs/hottest.json"


async def fetch_lobsters(top_n: int = 10) -> list[dict]:
    """抓取 Lobste.rs 热门帖子"""
    items = []
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(LOBSTERS_URL)
            posts = resp.json()

            for post in posts[:top_n]:
                items.append({
                    "title": post.get("title", ""),
                    "url": post.get("url", ""),
                    "comments_url": post.get("comments_url", ""),
                    "score": post.get("score", 0),
                    "comments": post.get("comment_count", 0),
                    "author": post.get("submitter_user", {}).get("username", ""),
                    "tags": post.get("tags") if isinstance(post.get("tags"), list) else [],
                    "source": "Lobsters",
                    "created": post.get("created_at", ""),
                })
        except Exception as e:
            print(f"Lobsters fetch error: {e}")

    return items


if __name__ == "__main__":
    import asyncio
    results = asyncio.run(fetch_lobsters())
    for item in results:
        print(f"[{item['score']}↑] {item['title'][:60]}")
