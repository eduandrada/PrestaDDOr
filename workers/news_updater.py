import os

def start_news_scheduler(app):
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from utils.news import fetch_latest_news
    except ImportError:
        return None
    if getattr(app, '_news_scheduler', None):
        return app._news_scheduler
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(fetch_latest_news, 'interval', minutes=5, id='news_refresh', replace_existing=True, max_instances=1, coalesce=True)
    scheduler.start()
    app._news_scheduler = scheduler
    return scheduler
