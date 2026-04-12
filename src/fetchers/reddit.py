"""
Reddit 抓取器 - 使用公开 JSON API（无需认证）
"""
import httpx
import asyncio

REDDIT_HOT_URL = "https://www.reddit.com/r/{}/hot.json?limit={}"
REDDIT_HEADERS = {"User-Agent": "DailyDigestBot/1.0"}


async def fetch_reddit(subreddits: list[str], top_n: int = 10) -> list[dict]:
    """抓取多个 subreddit 的热门帖子"""
    items = []
    seen = set()
    per_sub = max(top_n // len(subreddits), 5)

    async with httpx.AsyncClient(timeout=30, headers=REDDIT_HEADERS) as client:
        tasks = [client.get(REDDIT_HOT_URL.format(sub, per_sub + 5)) for sub in subreddits]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for sub, resp in zip(subreddits, responses):
            if isinstance(resp, Exception):
                continue
            try:
                data = resp.json()
                posts = data.get("data", {}).get("children", [])
                for post in posts:
                    p = post.get("data", {})
                    post_id = p.get("id", "")
                    if post_id in seen:
                        continue
                    seen.add(post_id)

                    # 过滤 pinned/stickied
                    if p.get("stickied"):
                        continue

                    items.append({
                        "title": p.get("title", ""),
                        "url": f"https://reddit.com{p.get('permalink', '')}",
                        "external_url": p.get("url", ""),
                        "score": p.get("score", 0),
                        "comments": p.get("num_comments", 0),
                        "subreddit": p.get("subreddit", sub),
                        "author": p.get("author", ""),
                        "source": f"Reddit r/{sub}",
                    })
            except Exception:
                continue

    # 按 score 排序
    items.sort(key=lambda x: x.get("score", 0), reverse=True)
    return items[:top_n]


if __name__ == "__main__":
    results = asyncio.run(fetch_reddit(["technology", "programming", "startups"]))
    for item in results:
        print(f"[{item['score']}↑] r/{item['subreddit']}: {item['title'][:60]}")
