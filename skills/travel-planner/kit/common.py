"""Shared helpers: polite HTTP with a cache, distances, dates."""
import hashlib, json, math, os, time, urllib.request, datetime

UA = "travel-planner/0.1 (Claude plug-in; github.com/CAFEERON21br18)"
CACHE = os.environ.get("TP_CACHE", os.path.expanduser("~/.cache/travel-planner"))
os.makedirs(CACHE, exist_ok=True)
_last = {}


def http(url, min_gap=0.0, binary=False, cache=True, timeout=30):
    """GET with a named user agent, a per-host pause and a disk cache."""
    key = os.path.join(CACHE, "http", hashlib.sha1(url.encode()).hexdigest())
    if cache and os.path.exists(key):
        b = open(key, "rb").read()
        return b if binary else b.decode()
    host = url.split("/")[2]
    wait = _last.get(host, 0) + min_gap - time.time()
    if wait > 0:
        time.sleep(wait)
    b = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout).read()
    _last[host] = time.time()
    if cache:
        os.makedirs(os.path.dirname(key), exist_ok=True)
        open(key, "wb").write(b)
    return b if binary else b.decode()


def km(a, b):
    """Great-circle distance between two [lon, lat] points."""
    (x1, y1), (x2, y2) = a, b
    p = math.pi / 180
    h = math.sin((y2 - y1) * p / 2) ** 2 + math.cos(y1 * p) * math.cos(y2 * p) * math.sin((x2 - x1) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def weekday(date):
    return WEEKDAYS[datetime.date.fromisoformat(date).weekday()]


def minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def load(path):
    return json.load(open(path, encoding="utf-8"))


def save(obj, path):
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
