# 📰 Daily Digest

> AI 驱动的每日科技热点聚合，全网信息一网打尽

比 newkit.site 更丰富：覆盖 **12+ 个平台**，自动生成中英双语摘要，每天定时发布。

---

## 🎯 覆盖的数据源

| 分类 | 来源 | 说明 |
|------|------|------|
| 🟠 科技社区 | Hacker News | 官方 API，Top 20 |
| 🦞 开发者 | Lobsters | JSON API |
| 👩‍💻 开发者 | Dev.to | 公开 API |
| 💬 中文社区 | V2EX | JSON API |
| 👽 论坛 | Reddit | technology/programming/startups/AI 等 6 个子版块 |
| ⭐ 开源 | GitHub Trending | 每日热门仓库 |
| 🚀 产品 | Product Hunt | 今日新产品 |
| 🐦 社交 | Twitter/X 趋势 | 通过 trends24.in |
| 📰 RSS | TechCrunch | RSS Feed |
| 📰 RSS | The Verge | RSS Feed |
| 📰 RSS | Ars Technica | RSS Feed |
| 📰 RSS | WIRED | RSS Feed |
| 📰 RSS | TechMeme | RSS Feed |
| 📰 中文 | 36氪 | RSS Feed |
| 📰 中文 | InfoQ | RSS Feed |

**总计：15 个数据源，每天 100-200+ 条内容**

---

## 🏗️ 技术架构

```
GitHub Actions (每天 09:00 CST 定时触发)
  │
  ├── 1. Python 抓取脚本 → 并发抓取 15 个平台
  ├── 2. AI 摘要生成 (DeepSeek/OpenAI) → 中英双语摘要
  ├── 3. 生成 Markdown 文件 → content/daily/YYYY-MM-DD.md
  ├── 4. 构建静态网站 → site/dist/
  └── 5. 部署 → GitHub Pages / Cloudflare Pages
```

**成本：¥0**（只需一个免费的 AI API key，每天约 0.1-0.5 元）

---

## 🚀 快速开始

### 1. Fork 或 Clone 仓库

```bash
git clone https://github.com/YOUR_USERNAME/daily-digest.git
cd daily-digest
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 本地测试

```bash
# 抓取数据（无 AI key 也能跑，只是没有摘要）
python3 -m src.main

# 构建网站
python3 site/build.py

# 预览
open site/dist/index.html
```

### 4. 配置 GitHub Secrets

在仓库 Settings → Secrets → Actions 中添加：

| Secret 名称 | 说明 | 是否必须 |
|------------|------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key（推荐，便宜） | 可选 |
| `OPENAI_API_KEY` | OpenAI API Key | 可选 |

> 不配置 AI key 也能用，只是摘要功能退化为直接列出标题。

### 5. 开启 GitHub Pages

仓库 Settings → Pages → Source 选择 "GitHub Actions"

### 6. 手动触发首次运行

Actions → Daily Digest → Run workflow

---

## 📁 项目结构

```
daily-digest/
├── .github/workflows/
│   └── daily.yml           # GitHub Actions 工作流
├── src/
│   ├── config.py           # 全局配置
│   ├── main.py             # 主入口
│   ├── fetchers/           # 各平台抓取器
│   │   ├── hackernews.py   # Hacker News
│   │   ├── github_trending.py
│   │   ├── reddit.py
│   │   ├── producthunt.py
│   │   ├── twitter_trends.py
│   │   ├── rss.py          # TechCrunch/The Verge/36kr 等
│   │   ├── lobsters.py
│   │   ├── devto.py
│   │   └── v2ex.py
│   └── processors/
│       └── summarizer.py   # AI 摘要生成
├── content/
│   └── daily/              # 每日生成的 Markdown + JSON
├── site/
│   ├── build.py            # 静态网站生成器
│   └── dist/               # 构建输出
├── requirements.txt
└── README.md
```

---

## ⚙️ 自定义配置

编辑 `src/config.py`：

```python
# 开关数据源
SOURCES = {
    "hackernews": {"enabled": True, "top_n": 20},
    "reddit": {"enabled": True, "top_n": 10, "subreddits": ["technology", "programming", "startups"]},
    # ...
}

# AI 配置
AI_PROVIDER = "deepseek"  # deepseek / openai / siliconflow
AI_MODEL = "deepseek-chat"

# 添加更多 RSS 源
RSS_FEEDS = {
    "techcrunch": "https://techcrunch.com/feed/",
    # 添加你的源...
}
```

---

## 🌐 部署到 Cloudflare Pages

除了 GitHub Pages，也可以部署到 Cloudflare Pages（免费、全球 CDN 更快）：

1. 登录 Cloudflare Dashboard → Pages
2. 连接 GitHub 仓库
3. 构建设置：
   - Build command: `python3 site/build.py`
   - Build output directory: `site/dist`
4. 绑定自定义域名（可选）

或者直接用 Wrangler CLI：

```bash
npm install -g wrangler
wrangler pages deploy site/dist --project-name daily-digest
```

---

## 📊 对比 newkit.site

| 特性 | newkit.site | Daily Digest |
|------|------------|--------------|
| 数据源 | 12 个 | 15 个 |
| 中文社区 | ❌ | ✅ V2EX、36氪、InfoQ |
| Reddit | ❌ | ✅ 6 个子版块 |
| Twitter/X | ❌ | ✅ 趋势 + 热门 |
| 产品发现 | Product Hunt | Product Hunt |
| 开源代码 | 未公开 | ✅ 完全开源 |
| 自定义 | ❌ | ✅ 可配置所有参数 |
| 数据下载 | ❌ | ✅ JSON 格式 |

---

## 📜 License

MIT
