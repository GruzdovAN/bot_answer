# Простой список каналов
CHANNELS = {
    "datascience_jobs": {
        "username": "@datasciencejobs",
        "enabled": True,
        "parser_type": "job_parser",
        "days_back": 7,
        "batch_size": 100
    },
    "python_jobs": {
        "username": "@python_jobs", 
        "enabled": True,
        "parser_type": "job_parser",
        "days_back": 30,
        "batch_size": 500
    },
    "tech_news": {
        "username": "@technews",
        "enabled": True,
        "parser_type": "news_parser", 
        "days_back": 7,
        "batch_size": 200
    }
}
