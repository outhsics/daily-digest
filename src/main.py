#!/usr/bin/env python3
"""
Daily Digest - 主入口
每日自动抓取 + AI 摘要 + 生成 Markdown
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import SOURCES, CONTENT_DIR, DATE_FORMAT, RSS_FEEDS
from src.fetchers.hackernews import fetch_hackernews
from src.fetchers.github_trending import fetch_github_trending
from src.fetchers.reddit import fetch_reddit
from src.fetchers.producthunt import fetch_producthunt
from src.fetchers.twitter_trends import fetch_twitter_trends
from src.fetchers.rss import fetch_all_rss
from src.fetchers.lobsters import fetch_lobsters
from src.fetchers.devto import fetch_devto
from src.fetchers.v2ex import fetch_v2ex
from src.processors.summarizer import generate_summary, generate_daily_briefing


def get_today() -> str:
    """获取今天日期（东八区）"""
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime(DATE_FORMAT)


async def fetch_all_sources() -> dict:
    """并发抓取所有信息源"""
    tasks = {}
    cfg = SOURCES

    if cfg["hackernews"]["enabled"]:
        tasks["Hacker News"] = fetch_hackernews(cfg["hackernews"]["top_n"])

    if cfg["github_trending"]["enabled"]:
        tasks["GitHub Trending"] = fetch_github_trending(cfg["github_trending"]["top_n"])

    if cfg["reddit"]["enabled"]:
        tasks["Reddit"] = fetch_reddit(
            cfg["reddit"]["subreddits"],
            cfg["reddit"]["top_n"],
        )

    if cfg["producthunt"]["enabled"]:
        tasks["Product Hunt"] = fetch_producthunt(cfg["producthunt"]["top_n"])

    if cfg["twitter_trends"]["enabled"]:
        tasks["Twitter/X"] = fetch_twitter_trends(cfg["twitter_trends"]["top_n"])

    if cfg["lobsters"]["enabled"]:
        tasks["Lobsters"] = fetch_lobsters(cfg["lobsters"]["top_n"])

    if cfg["devto"]["enabled"]:
        tasks["Dev.to"] = fetch_devto(cfg["devto"]["top_n"])

    if cfg.get("v2ex", {}).get("enabled", True):
        tasks["V2EX"] = fetch_v2ex(10)

    # RSS 源
    rss_enabled = {k: v for k, v in RSS_FEEDS.items() if cfg.get(f"rss_{k}", {}).get("enabled", True)}
    if rss_enabled:
        rss_top = cfg.get("rss_techcrunch", {}).get("top_n", 10)
        tasks["RSS聚合"] = fetch_all_rss(rss_enabled, rss_top)

    # 并发执行
    results = {}
    completed = await asyncio.gather(*tasks.values(), return_exceptions=True)
    for name, result in zip(tasks.keys(), completed):
        if isinstance(result, Exception):
            print(f"  ✗ {name}: {result}")
            results[name] = []
        else:
            print(f"  ✓ {name}: {len(result)} items")
            results[name] = result

    return results


def generate_markdown(date_str: str, all_data: dict, summaries: dict, briefing: str) -> str:
    """生成完整的每日 Markdown 文档"""
    lines = []

    # 头部
    lines.append(f"# Daily Digest - {date_str}")
    lines.append("")
    lines.append(f"> 自动生成于 {datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')} CST")
    lines.append(f"> 数据源：{len(all_data)} 个平台，共 {sum(len(v) for v in all_data.values())} 条内容")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 每日简报
    lines.append("## 📌 今日要点")
    lines.append("")
    lines.append(briefing)
    lines.append("")
    lines.append("---")
    lines.append("")

    # 各板块内容
    section_emoji = {
        "Hacker News": "🟠",
        "GitHub Trending": "⭐",
        "Reddit": "👽",
        "Product Hunt": "🚀",
        "Twitter/X": "🐦",
        "Lobsters": "🦞",
        "Dev.to": "👩‍💻",
        "V2EX": "💬",
        "RSS聚合": "📰",
    }

    # 按数据量排序板块
    sorted_sections = sorted(all_data.items(), key=lambda x: len(x[1]), reverse=True)

    for source, items in sorted_sections:
        if not items:
            continue

        emoji = section_emoji.get(source, "📰")
        lines.append(f"## {emoji} {source}")
        lines.append("")

        # 优先显示 AI 摘要
        summary = summaries.get(source, "")
        if summary:
            lines.append(summary)
            lines.append("")

        # 原始列表
        lines.append("<details>")
        lines.append(f"<summary>📋 完整列表 ({len(items)} 条)</summary>")
        lines.append("")

        for i, item in enumerate(items[:15], 1):
            title = item.get("title", "")
            url = item.get("url", "")
            score = item.get("score", "") or item.get("reactions", "") or item.get("votes", "") or item.get("replies", "")
            score_str = f" `↑{score}`" if score else ""
            lang = item.get("language", "")
            lang_str = f" `{lang}`" if lang else ""
            desc = item.get("description", "") or item.get("summary", "")
            desc_str = f" — {desc[:100]}" if desc else ""

            lines.append(f"{i}. [{title}]({url}){score_str}{lang_str}{desc_str}")

        lines.append("")
        lines.append("</details>")
        lines.append("")
        lines.append("---")
        lines.append("")

    # 尾部
    lines.append("---")
    lines.append("")
    lines.append("*Generated by [Daily Digest](https://github.com) · Powered by GitHub Actions + AI*")

    return "\n".join(lines)


async def main():
    date_str = get_today()
    print(f"📰 Daily Digest - {date_str}")
    print("=" * 50)

    # 1. 抓取所有数据源
    print("\n🔄 正在抓取数据...")
    all_data = await fetch_all_sources()

    total = sum(len(v) for v in all_data.values())
    print(f"\n✅ 共抓取 {total} 条内容")

    if total == 0:
        print("❌ 没有抓取到任何内容，退出")
        return

    # 2. AI 摘要生成
    print("\n🤖 正在生成 AI 摘要...")
    summaries = {}
    for source, items in all_data.items():
        if items:
            summary = await generate_summary(items, source)
            summaries[source] = summary
            print(f"  ✓ {source}")

    # 3. 生成每日简报
    print("\n📝 正在生成每日简报...")
    briefing = await generate_daily_briefing(all_data)

    # 4. 生成 Markdown
    print("\n📄 正在生成 Markdown...")
    md_content = generate_markdown(date_str, all_data, summaries, briefing)

    # 5. 保存文件
    output_dir = Path(CONTENT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{date_str}.md"
    output_file.write_text(md_content, encoding="utf-8")
    print(f"\n✅ 已保存到 {output_file}")

    # 6. 同时保存原始 JSON 数据
    json_file = output_dir / f"{date_str}.json"
    json_data = {}
    for source, items in all_data.items():
        json_data[source] = items
    json_file.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 原始数据保存到 {json_file}")


if __name__ == "__main__":
    asyncio.run(main())
