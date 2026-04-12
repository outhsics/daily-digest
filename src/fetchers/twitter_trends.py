"""
Twitter/X 趋势抓取器 - 通过第三方 API 和趋势网站
"""
import httpx
import asyncio
from selectolax.parser import HTMLParser


async def fetch_twitter_trends(top_n: int = 15) -> list[dict]:
    """
    抓取 Twitter/X 热门话题
    使用多种数据源作为 fallback
    """
    items = []

    # 方法1: 尝试从 trends24.in 获取趋势
    async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as client:
        try:
            resp = await client.get("https://trends24.in/")
            tree = HTMLParser(resp.text)
            trend_cards = tree.css(".trend-card__list li a")
            seen = set()
            for el in trend_cards[:top_n * 2]:
                try:
                    text = el.text(strip=True)
                    href = el.attributes.get("href", "")
                    if not text or text in seen:
                        continue
                    seen.add(text)
                    items.append({
                        "title": text,
                        "url": f"https://twitter.com/search?q={text.replace('#', '%23')}",
                        "source": "Twitter/X 趋势",
                    })
                except Exception:
                    continue
        except Exception as e:
            print(f"trends24.in error: {e}")

    # 方法2: 从 getdaytrends 补充
    if len(items) < 5:
        try:
            async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as client:
                resp = await client.get("https://getdaytrends.com/")
                tree = HTMLParser(resp.text)
                for row in tree.css("table.trends tr"):
                    link = row.css_first("td a")
                    if link:
                        text = link.text(strip=True)
                        href = link.attributes.get("href", "")
                        if text:
                            items.append({
                                "title": text,
                                "url": f"https://twitter.com/search?q={text.replace('#', '%23')}",
                                "source": "Twitter/X 趋势",
                            })
        except Exception as e:
            print(f"getdaytrends error: {e}")

    # 方法3: 技术类热门推文（从 Nitter 替代源）
    if len(items) < 5:
        try:
            nitter_feeds = [
                "https://nitter.privacydev.net/search/rss?f=tweets&q=AI+OR+GPT+OR+LLM+OR+startup",
            ]
            async with httpx.AsyncClient(timeout=20, headers={"User-Agent": "Mozilla/5.0"}) as client:
                for feed_url in nitter_feeds:
                    try:
                        resp = await client.get(feed_url)
                        tree = HTMLParser(resp.text)
                        for item in tree.css("item")[:top_n]:
                            title_el = item.css_first("title")
                            link_el = item.css_first("link")
                            if title_el:
                                items.append({
                                    "title": title_el.text(strip=True)[:200],
                                    "url": link_el.text(strip=True) if link_el else "",
                                    "source": "Twitter/X 热门",
                                })
                    except Exception:
                        continue
        except Exception:
            pass

    return items[:top_n]


if __name__ == "__main__":
    results = asyncio.run(fetch_twitter_trends())
    for item in results:
        print(f"🐦 {item['title'][:80]}")
