import arrow
import feedparser
from lxml import html

from rsserpent_rev.utils import HTTPClient


async def get_changelog(pod: str):
    url = f"https://cocoapods.org/pods/{pod}"
    async with HTTPClient() as client:
        pod_resp = await client.get(url)
        if pod_resp.status_code == 200:
            html_text = pod_resp.content.decode("utf-8")
            tree = html.fromstring(html_text)
            home_link = tree.xpath("//ul[@class='links']")[0].xpath(".//li")[1].xpath(".//a")[0].attrib["href"]
            # is github repo link
            if home_link.startswith("https://github.com"):
                return get_changelog_by_url(pod, home_link)

    return None


def get_changelog_by_url(pod: str, url: str):
    feed = feedparser.parse(url + "/releases.atom")
    if len(feed.entries) == 0:
        return None

    return {
        "title": f"{pod} Changelog",
        "link": feed.feed.link,
        "description": feed.feed.title,
        "items": [
            {
                "title": x.title,
                "description": x.content[0].value,
                "link": x.link,
                "pub_date": arrow.get(x.updated),
            }
            for x in feed.entries
        ],
    }
