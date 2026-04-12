"""
Daily Digest - 全局配置
"""

# ===== 信息源开关 =====
SOURCES = {
    "hackernews": {"enabled": True, "top_n": 20},
    "github_trending": {"enabled": True, "top_n": 15},
    "reddit": {"enabled": True, "top_n": 10, "subreddits": ["technology", "programming", "startups", "entrepreneur", "SideProject", "artificial"]},
    "producthunt": {"enabled": True, "top_n": 10},
    "twitter_trends": {"enabled": True, "top_n": 15},
    "rss_techcrunch": {"enabled": True, "top_n": 10},
    "rss_theverge": {"enabled": True, "top_n": 10},
    "rss_ars": {"enabled": True, "top_n": 10},
    "rss_wired": {"enabled": True, "top_n": 8},
    "rss_techmeme": {"enabled": True, "top_n": 10},
    "rss_36kr": {"enabled": True, "top_n": 10},
    "rss_infoq": {"enabled": True, "top_n": 8},
    "lobsters": {"enabled": True, "top_n": 10},
    "devto": {"enabled": True, "top_n": 10},
}

# ===== AI 配置 =====
AI_PROVIDER = "deepseek"  # deepseek / openai / siliconflow
AI_MODEL = "deepseek-chat"
AI_BASE_URL = "https://api.deepseek.com"
AI_API_KEY_ENV = "DEEPSEEK_API_KEY"  # 环境变量名

# ===== RSS 源 =====
RSS_FEEDS = {
    "techcrunch": "https://techcrunch.com/feed/",
    "theverge": "https://www.theverge.com/rss/index.xml",
    "ars": "https://feeds.arstechnica.com/arstechnica/index",
    "wired": "https://www.wired.com/feed/rss",
    "techmeme": "https://www.techmeme.com/feed.xml",
    "36kr": "https://36kr.com/feed",
    "infoq": "https://www.infoq.cn/feed",
}

# ===== 输出配置 =====
CONTENT_DIR = "content/daily"
DATE_FORMAT = "%Y-%m-%d"
