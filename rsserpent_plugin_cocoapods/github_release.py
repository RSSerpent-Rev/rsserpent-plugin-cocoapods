import feedparser
from lxml import html

from rsserpent_rev.utils import HTTPClient
from feedparser_to_feedgen import to_feedgen
from feedgen.feed import FeedGenerator


async def get_changelog(pod: str) -> FeedGenerator | None:
    url = f"https://cocoapods.org/pods/{pod}"
    async with HTTPClient() as client:
        pod_resp = await client.get(url)
        if pod_resp.status_code == 200:
            html_text = pod_resp.content.decode("utf-8")
            tree = html.fromstring(html_text)
            home_link = tree.xpath("//ul[@class='links']")[0].xpath(".//li")[1].xpath(".//a")[0].attrib["href"]
            # is github repo link
            if home_link.startswith("https://github.com"):
                return get_changelog_by_url(home_link)

    return None


def get_changelog_by_url(url: str) -> FeedGenerator:
    feed = feedparser.parse(url + "/releases.atom")
    return to_feedgen(feed)
