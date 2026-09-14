import json
import os
import time
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import requests

CACHE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'news_cache.json'))
DEFAULT_CATEGORIES = ['Catamarca', 'política Catamarca', 'policiales Catamarca']
DEFAULT_FEEDS = [
    'https://news.google.com/rss/search?q=Catamarca+pol%C3%ADtica&hl=es-419&gl=AR&ceid=AR:es-419',
    'https://news.google.com/rss/search?q=Catamarca+policiales&hl=es-419&gl=AR&ceid=AR:es-419',
    'https://news.google.com/rss/search?q=Catamarca+Argentina&hl=es-419&gl=AR&ceid=AR:es-419',
]

def _load_news_config():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'settings.json'))
    cfg = {}
    try:
        with open(path, encoding='utf-8') as f: cfg = json.load(f) or {}
    except Exception: pass
    raw = str(cfg.get('news_categories') or ','.join(DEFAULT_CATEGORIES))
    categories = [x.strip() for x in raw.replace(';', ',').split(',') if x.strip()] or DEFAULT_CATEGORIES
    limit = max(5, min(50, int(cfg.get('news_limit', 20) or 20)))
    custom = [x.strip() for x in str(cfg.get('news_custom_feed') or '').splitlines() if x.strip().startswith(('http://','https://'))]
    enabled = cfg.get('news_enabled', True) is not False
    try:
        source_filters = [str(x).strip() for x in (cfg.get('news_source_blocklist') or []) if str(x).strip()]
    except Exception:
        source_filters = []
    return categories, limit, custom, enabled, source_filters

def _feed_urls():
    categories, limit, custom, enabled, source_filters = _load_news_config()
    if not enabled: return [], limit, source_filters
    urls = []
    for category in categories:
        query = requests.utils.quote(category)
        urls.append(f'https://news.google.com/rss/search?q={query}&hl=es-419&gl=AR&ceid=AR:es-419')
    urls.extend(custom)
    return list(dict.fromkeys(urls)), limit, source_filters


def _parse(xml_text, source):
    root = ET.fromstring(xml_text)
    out=[]
    for item in root.findall('.//item')[:10]:
        title=(item.findtext('title') or '').strip()
        link=(item.findtext('link') or '').strip()
        pub=(item.findtext('pubDate') or '').strip()
        source_node = item.find('source')
        source_name = (source_node.text or '').strip() if source_node is not None else ''
        source_url = (source_node.attrib.get('url') or '').strip() if source_node is not None else ''
        if not title or not link: continue
        try: published=parsedate_to_datetime(pub).isoformat() if pub else ''
        except Exception: published=pub
        out.append({'title':title,'link':link,'published':published,'source':source_name or source,'source_url':source_url})
    return out


def fetch_latest_news():
    urls, limit, source_filters = _feed_urls()
    if not urls:
        return []
    items=[]
    for url in urls:
        try:
            r=requests.get(url, timeout=8, headers={'User-Agent':'PrestamosNews/1.0'})
            r.raise_for_status()
            source='Google News / Catamarca'
            items.extend(_parse(r.text, source))
        except Exception:
            continue
    seen=set(); unique=[]
    for item in items:
        key=item['title'].lower()
        if key not in seen:
            seen.add(key); unique.append(item)
    if source_filters:
        blocked = {x.casefold() for x in source_filters}
        unique = [item for item in unique if str(item.get('source') or '').casefold() not in blocked]
    unique=unique[:limit]
    if unique:
        payload={'updated_at':time.time(),'items':unique}
        try:
            with open(CACHE_PATH,'w',encoding='utf-8') as f: json.dump(payload,f,ensure_ascii=False,indent=2)
        except OSError: pass
        return unique
    return get_cached_news()


def get_cached_news():
    try:
        with open(CACHE_PATH,encoding='utf-8') as f: return json.load(f).get('items',[])
    except Exception: return []
