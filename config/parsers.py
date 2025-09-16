# Простые настройки парсеров
PARSERS = {
    "job_parser": {
        "extract_hashtags": True,
        "extract_mentions": True,
        "extract_links": True,
        "extract_technologies": True,
        "technologies": [
            "python", "javascript", "java", "c++", "c#",
            "react", "angular", "vue", "node.js", "django",
            "flask", "fastapi", "spring", "hibernate",
            "postgresql", "mysql", "mongodb", "redis",
            "docker", "kubernetes", "aws", "azure", "gcp",
            "machine learning", "data science", "ai", "ml"
        ]
    },
    "news_parser": {
        "extract_hashtags": True,
        "extract_mentions": True,
        "extract_links": True,
        "extract_companies": True,
        "companies": [
            "Google", "Apple", "Microsoft", "Amazon", "Meta",
            "Tesla", "Netflix", "Uber", "Airbnb", "Spotify",
            "OpenAI", "Anthropic", "Stripe", "Shopify"
        ]
    }
}
