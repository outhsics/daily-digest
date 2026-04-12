#!/usr/bin/env python3
"""
Daily Digest - 静态网站生成器
读取 content/daily/*.md → 生成 site/dist/*.html
零依赖，纯 Python + markdown2
"""
import os
import re
import glob
import json
from datetime import datetime
from pathlib import Path

try:
    import markdown
    def md_to_html(text):
        return markdown.markdown(text, extensions=["fenced_code", "tables", "toc"])
except ImportError:
    try:
        import markdown2
        def md_to_html(text):
            return markdown2.markdown(text, extras=["fenced-code-blocks", "tables"])
    except ImportError:
        # 纯 Python fallback：简单的 markdown 转 HTML
        def md_to_html(text):
            import re
            # Headers
            text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
            text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
            text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
            text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
            # Bold
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            # Links
            text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
            # Lists
            text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
            text = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', text, flags=re.MULTILINE)
            # Paragraphs
            text = re.sub(r'\n\n+', '</p><p>', text)
            text = f'<p>{text}</p>'
            # Blockquote
            text = re.sub(r'^&gt; (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
            # Code
            text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
            # HR
            text = re.sub(r'^---$', '<hr>', text, flags=re.MULTILINE)
            return text


# ===== 配置 =====
CONTENT_DIR = Path(__file__).parent.parent / "content" / "daily"
OUTPUT_DIR = Path(__file__).parent / "dist"
SITE_TITLE = "Daily Digest"
SITE_SUBTITLE = "每日科技热点聚合 · AI 驱动的新闻日报"
SITE_URL = ""  # 部署后填写


def get_css() -> str:
    return """
:root {
  --bg: #0d1117;
  --bg-card: #161b22;
  --bg-hover: #1c2333;
  --text: #e6edf3;
  --text-muted: #8b949e;
  --accent: #58a6ff;
  --accent-green: #3fb950;
  --border: #30363d;
  --orange: #f0883e;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  padding: 40px 20px 30px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 30px;
}

header h1 {
  font-size: 2rem;
  margin-bottom: 8px;
  background: linear-gradient(135deg, var(--accent), #a371f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

header p {
  color: var(--text-muted);
  font-size: 0.95rem;
}

/* 导航 */
.nav-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  list-style: none;
  margin-top: 20px;
}

.nav-list a {
  color: var(--text-muted);
  text-decoration: none;
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--border);
  font-size: 0.85rem;
  transition: all 0.2s;
}

.nav-list a:hover {
  color: var(--accent);
  border-color: var(--accent);
}

/* 日期列表页 */
.date-grid {
  display: grid;
  gap: 12px;
}

.date-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px 24px;
  text-decoration: none;
  color: var(--text);
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date-card:hover {
  background: var(--bg-hover);
  border-color: var(--accent);
  transform: translateY(-1px);
}

.date-card .date {
  font-size: 1.2rem;
  font-weight: 600;
}

.date-card .meta {
  color: var(--text-muted);
  font-size: 0.85rem;
}

/* 文章页 */
article h1 {
  font-size: 1.6rem;
  margin: 30px 0 10px;
}

article h2 {
  font-size: 1.3rem;
  margin: 35px 0 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
  color: var(--accent);
}

article h3 {
  font-size: 1.1rem;
  margin: 25px 0 10px;
}

article p {
  margin: 10px 0;
  color: var(--text);
}

article a {
  color: var(--accent);
  text-decoration: none;
}

article a:hover {
  text-decoration: underline;
}

article blockquote {
  border-left: 3px solid var(--accent);
  padding: 10px 15px;
  margin: 15px 0;
  background: var(--bg-card);
  border-radius: 0 8px 8px 0;
  color: var(--text-muted);
}

article ul, article ol {
  padding-left: 25px;
  margin: 10px 0;
}

article li {
  margin: 6px 0;
  color: var(--text);
}

article li a {
  color: var(--accent);
}

article hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 25px 0;
}

article code {
  background: var(--bg-card);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}

article details {
  margin: 15px 0;
}

article summary {
  cursor: pointer;
  color: var(--text-muted);
  font-size: 0.9rem;
  padding: 8px 0;
}

article details[open] summary {
  margin-bottom: 10px;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  background: rgba(88,166,255,0.15);
  color: var(--accent);
}

/* 返回顶部 */
.back-link {
  display: inline-block;
  margin: 20px 0;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.9rem;
}

.back-link:hover { color: var(--accent); }

/* 页脚 */
footer {
  text-align: center;
  padding: 30px 20px;
  color: var(--text-muted);
  font-size: 0.8rem;
  border-top: 1px solid var(--border);
  margin-top: 40px;
}

/* 响应式 */
@media (max-width: 600px) {
  .container { padding: 15px; }
  header h1 { font-size: 1.5rem; }
  article h2 { font-size: 1.1rem; }
  .date-card { padding: 15px; }
}
"""


def get_page_html(title: str, body: str, is_article: bool = False) -> str:
    """生成完整 HTML 页面"""
    nav = """
    <nav>
      <ul class="nav-list">
        <li><a href="index.html">📅 所有日报</a></li>
      </ul>
    </nav>
    """ if not is_article else ""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - {SITE_TITLE}</title>
  <style>{get_css()}</style>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📰</text></svg>">
</head>
<body>
  <div class="container">
    <header>
      <h1>📰 {SITE_TITLE}</h1>
      <p>{SITE_SUBTITLE}</p>
    </header>
    {nav}
    <main>
      {body}
    </main>
    <footer>
      <p>Powered by GitHub Actions + AI · 自动生成</p>
      <p>Data from Hacker News, GitHub, Reddit, Twitter/X, Product Hunt, V2EX, and more</p>
    </footer>
  </div>
</body>
</html>"""


def build_index(dates: list[tuple[str, int, str]]) -> str:
    """生成首页 HTML"""
    cards = ""
    for date_str, count, preview in dates:
        preview_text = preview[:80] + "..." if len(preview) > 80 else preview
        cards += f"""
      <a class="date-card" href="{date_str}.html">
        <div>
          <div class="date">📅 {date_str}</div>
          <div class="meta">{preview_text}</div>
        </div>
        <div class="meta">{count} 条内容 →</div>
      </a>"""

    body = f"""
    <div class="date-grid">
      {cards}
    </div>
    """
    return get_page_html("首页", body)


def build_article(date_str: str, md_content: str) -> str:
    """将 Markdown 转为文章 HTML"""
    html_content = md_to_html(md_content)
    back_link = '<a class="back-link" href="index.html">← 返回所有日报</a>'
    body = f"""
    {back_link}
    <article>
      {html_content}
    </article>
    {back_link}
    """
    return get_page_html(date_str, body, is_article=True)


def parse_markdown_info(filepath: Path) -> tuple[str, int, str]:
    """从 Markdown 文件提取日期、条目数、预览文字"""
    content = filepath.read_text(encoding="utf-8")
    date_str = filepath.stem  # 文件名就是日期
    # 统计列表条目数
    count = len(re.findall(r'^\d+\.', content, re.MULTILINE))
    # 提取第一行非空内容作为预览
    preview = ""
    for line in content.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith(">") and not line.startswith("---"):
            preview = re.sub(r'[*`#\[\]()]', '', line)
            break
    return date_str, count, preview


def main():
    print("🏗️  Building static site...")

    # 确保内容目录存在
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 查找所有 Markdown 文件
    md_files = sorted(CONTENT_DIR.glob("*.md"), reverse=True)
    if not md_files:
        print("⚠️  No markdown files found in content/daily/")
        # 生成一个示例页面
        sample = """# Daily Digest - 示例

> 这是一个示例日报

## 📌 今日要点

等待 GitHub Actions 首次运行生成内容...

## 🟠 Hacker News

- 等待数据...

## ⭐ GitHub Trending

- 等待数据...

---
*Generated by Daily Digest*
"""
        sample_file = CONTENT_DIR / "2026-01-01.md"
        sample_file.write_text(sample, encoding="utf-8")
        md_files = [sample_file]

    # 构建日期列表
    dates = []
    for md_file in md_files:
        date_str, count, preview = parse_markdown_info(md_file)
        dates.append((date_str, count, preview))

    # 生成首页
    index_html = build_index(dates)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"  ✓ index.html ({len(dates)} days)")

    # 生成每日页面
    for md_file in md_files:
        date_str = md_file.stem
        md_content = md_file.read_text(encoding="utf-8")
        html = build_article(date_str, md_content)
        (OUTPUT_DIR / f"{date_str}.html").write_text(html, encoding="utf-8")
        print(f"  ✓ {date_str}.html")

    # 复制 JSON 数据文件
    for json_file in CONTENT_DIR.glob("*.json"):
        import shutil
        shutil.copy2(json_file, OUTPUT_DIR / json_file.name)
        print(f"  ✓ {json_file.name}")

    print(f"\n✅ Site built in {OUTPUT_DIR}")
    print(f"   {len(md_files)} pages generated")


if __name__ == "__main__":
    main()
