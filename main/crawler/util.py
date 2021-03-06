import logging
import time
from urllib import parse

import get_retries
from django.utils import text
from url_normalize import url_normalize

logger = logging.getLogger(__name__)


def fetch(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"
    }
    return get_retries.get(url, headers=headers)


def create_abs_urls(urls, base_url):
    """create absolute URLs and only normalize
    """
    res = []
    for l in urls:
        try:
            l = url_normalize(l)
            x = parse.urljoin(base_url, l)
            res.append(x)
        except:
            pass
    return res


# https://stackoverflow.com/a/12170628/4028896
# removed the 'rss' extension because we are looking for it
IGNORED_EXTENSIONS = [
    # images
    "mng",
    "pct",
    "bmp",
    "gif",
    "jpg",
    "jpeg",
    "png",
    "pst",
    "psp",
    "tif",
    "tiff",
    "ai",
    "drw",
    "dxf",
    "eps",
    "ps",
    "svg",
    # audio
    "mp3",
    "wma",
    "ogg",
    "wav",
    "ra",
    "aac",
    "mid",
    "au",
    "aiff",
    # video
    "3gp",
    "asf",
    "asx",
    "avi",
    "mov",
    "mp4",
    "mpg",
    "qt",
    "rm",
    "swf",
    "wmv",
    "m4a",
    # other
    "css",
    "pdf",
    "doc",
    "exe",
    "bin",
    "zip",
    "rar",
]


def internal_urls(urls, base_url):
    res = set()
    orig_loc = parse.urlparse(base_url).netloc

    urls = create_abs_urls(urls, base_url)

    for u in urls:
        parsed = parse.urlparse(u)

        # make sure to also include subdomains
        u_loc = parsed.netloc
        if not u_loc.endswith(orig_loc) or orig_loc.endswith(u_loc):
            continue

        if any(parsed.path.endswith("." + x) for x in IGNORED_EXTENSIONS):
            logger.debug(f"skip link: {u}")
            continue

        # normalized (again) use only scheme, netloc and path
        normalized = parse.urlunparse(parsed[:3] + ("", "", ""))
        res.add(normalized)

    return list(res)


def external_base_urls(urls):
    """Filter from Wikipedia pages extracted urls
    """
    # filter all internal urls
    urls = [
        l
        for l in urls
        if any(l.startswith(scheme) for scheme in ("//", "http", "https"))
    ]

    res = []
    for l in urls:
        parsed = parse.urlparse(url_normalize(l))
        netloc = parsed.netloc
        if any(
            wiki in netloc
            for wiki in ("wikipedia", "wikidata", "wikimedia", "mediawiki")
        ):
            logger.debug(f"skip: {l}")
            continue

        if any(parsed.path.endswith("." + x) for x in IGNORED_EXTENSIONS):
            logger.debug(f"skip: {l}")
            continue

        base = parse.urlunparse(parsed[:2] + ("", "", "", ""))
        res.append(base)
    return list(set(res))  # unique


def slugify(url):
    url = url.split("https://")[-1]
    url = url.split("http://")[-1]

    if url.startswith("www"):
        url = url[3:]
    return text.slugify(url)
