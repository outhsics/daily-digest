"""
GitHub Trending 抓取器
"""
import httpx
from selectolax.parser import HTMLParser
from datetime import datetime

GITHUB_TRENDING_URL = "https://github.com/trending"
LANGUAGES = ["", "python", "javascript", "typescript", "go", "rust", "java"]
PERIODS = ["daily"]


async def fetch_github_trending(top_n: int = 15) -> list[dict]:
    """抓取 GitHub Trending 仓库"""
    items = []
    seen = set()
    async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for period in PERIODS:
            url = f"{GITHUB_TRENDING_URL}?since={period}"
            try:
                resp = await client.get(url)
                tree = HTMLParser(resp.text)

                for article in tree.css("article.Box-row"):
                    try:
                        # 仓库名
                        h2 = article.css_first("h2 a")
                        if not h2:
                            continue
                        repo_name = h2.attributes.get("href", "").strip("/")
                        if repo_name in seen:
                            continue
                        seen.add(repo_name)

                        # 描述
                        p = article.css_first("p")
                        description = p.text(strip=True) if p else ""

                        # 语言
                        lang_span = article.css_first("[itemprop='programmingLanguage']")
                        language = lang_span.text(strip=True) if lang_span else ""

                        # Stars today
                        stars_today = ""
                        for span in article.css("span.d-inline-block.float-sm-right"):
                            stars_today = span.text(strip=True)
                            break

                        # 总 Stars
                        star_links = article.css("a.Link--muted.d-inline-block.mr-3")
                        total_stars = star_links[0].text(strip=True) if star_links else ""

                        items.append({
                            "repo": repo_name,
                            "url": f"https://github.com/{repo_name}",
                            "description": description,
                            "language": language,
                            "total_stars": total_stars,
                            "stars_today": stars_today,
                            "source": "GitHub Trending",
                            "period": period,
                        })
                    except Exception:
                        continue
            except Exception as e:
                print(f"GitHub Trending fetch error: {e}")
                continue

    return items[:top_n]


if __name__ == "__main__":
    import asyncio
    results = asyncio.run(fetch_github_trending())
    for item in results:
        print(f"⭐ {item['repo']} - {item['description'][:60]}")
