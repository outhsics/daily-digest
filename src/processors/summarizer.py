"""
AI 摘要生成器
"""
import httpx
import json
import os
from src.config import AI_PROVIDERS


def _get_active_provider() -> dict | None:
    """找到第一个有 API key 的 AI 提供商"""
    import os
    for provider in AI_PROVIDERS:
        key = os.environ.get(provider["env_key"], "")
        if key:
            return {**provider, "key": key}
    return None


async def generate_summary(items: list[dict], source_name: str) -> str:
    """对一批新闻条目生成中文摘要"""
    if not items:
        return ""

    # 构建 prompt
    items_text = ""
    for i, item in enumerate(items[:20], 1):
        title = item.get("title", "")
        url = item.get("url", "")
        desc = item.get("description", "") or item.get("summary", "")
        score = item.get("score", "") or item.get("reactions", "") or item.get("votes", "")
        score_str = f" (↑{score})" if score else ""
        items_text += f"{i}. {title}{score_str}\n   {desc[:150]}\n   {url}\n\n"

    prompt = f"""你是科技新闻编辑。请为以下来自 {source_name} 的热门内容生成简洁的中文摘要。

要求：
1. 按重要性排序，挑选最有价值的 {min(len(items), 10)} 条
2. 每条用一句话概括核心信息（中文）
3. 保留原文链接
4. 格式：**标题**：一句话描述

内容：
{items_text}"""

    provider = _get_active_provider()
    if not provider:
        return _fallback_summary(items, source_name)

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{provider['base_url']}/chat/completions",
                headers={"Authorization": f"Bearer {provider['key']}", "Content-Type": "application/json"},
                json={
                    "model": provider["model"],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                },
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI summary error ({provider['name']}): {e}")
        return _fallback_summary(items, source_name)


async def generate_daily_briefing(all_sections: dict[str, list[dict]]) -> str:
    """生成每日综合简报"""
    # 收集所有标题
    highlights = []
    for source, items in all_sections.items():
        for item in items[:3]:
            highlights.append(f"[{source}] {item.get('title', '')}")

    prompt = f"""你是资深科技编辑。根据今天的科技新闻，写一份每日科技简报。

要求：
1. 提炼 3-5 个今日最值得关注的趋势/事件
2. 每个趋势用 2-3 句话说明
3. 语言简洁有力，适合快速阅读
4. 中文输出

今日各平台热门标题：
{chr(10).join(highlights[:30])}"""

    provider = _get_active_provider()
    if not provider:
        return _fallback_briefing(all_sections)

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{provider['base_url']}/chat/completions",
                headers={"Authorization": f"Bearer {provider['key']}", "Content-Type": "application/json"},
                json={
                    "model": provider["model"],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 1500,
                },
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI briefing error ({provider['name']}): {e}")
        return _fallback_briefing(all_sections)


def _fallback_summary(items: list[dict], source_name: str) -> str:
    """无 AI 时的 fallback：直接列出标题"""
    lines = []
    for item in items[:10]:
        title = item.get("title", "")
        url = item.get("url", "")
        score = item.get("score", "") or item.get("reactions", "") or item.get("votes", "")
        score_str = f" (↑{score})" if score else ""
        lines.append(f"- **{title}**{score_str}\n  {url}")
    return "\n".join(lines)


def _fallback_briefing(all_sections: dict) -> str:
    """无 AI 时的 fallback 简报"""
    return "## 今日要点\n\n各平台热门内容已聚合，详见下方各板块。\n"
