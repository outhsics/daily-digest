"""
Product Hunt 抓取器 - 网页抓取
"""
import httpx
from selectolax.parser import HTMLParser

PH_URL = "https://www.producthunt.com/"


async def fetch_producthunt(top_n: int = 10) -> list[dict]:
    """抓取 Product Hunt 今日热门产品"""
    items = []
    async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as client:
        try:
            resp = await client.get(PH_URL)
            tree = HTMLParser(resp.text)

            # 尝试从页面提取产品信息
            for link in tree.css("a[data-test='post-name']"):
                try:
                    title = link.text(strip=True)
                    href = link.attributes.get("href", "")
                    if not title or not href:
                        continue
                    url = f"https://www.producthunt.com{href}" if href.startswith("/") else href

                    # 尝试获取 votes
                    parent = link.parent
                    votes = ""
                    if parent:
                        vote_el = parent.css_first("[data-test='vote-button']")
                        if vote_el:
                            votes = vote_el.text(strip=True)

                    items.append({
                        "title": title,
                        "url": url,
                        "votes": votes,
                        "source": "Product Hunt",
                    })
                except Exception:
                    continue

        except Exception as e:
            print(f"Product Hunt fetch error: {e}")
            # fallback: 尝试 RSS
            try:
                rss_resp = await client.get("https://www.producthunt.com/feed")
                tree = HTMLParser(rss_resp.text)
                for item in tree.css("item"):
                    title_el = item.css_first("title")
                    link_el = item.css_first("link")
                    if title_el:
                        items.append({
                            "title": title_el.text(strip=True),
                            "url": link_el.text(strip=True) if link_el else "",
                            "source": "Product Hunt",
                        })
            except Exception:
                pass

    return items[:top_n]


if __name__ == "__main__":
    import asyncio
    results = asyncio.run(fetch_producthunt())
    for item in results:
        print(f"🚀 {item['title']} - {item.get('votes', 'N/A')} votes")
