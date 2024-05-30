from typing import Any

import arrow
from lxml import html

from rsserpent_rev.utils import HTTPClient

path = "/admob/sdk-update/{platform}"


def get_date(date_str: str) -> arrow.Arrow:
    formats = ["YYYY-MM-DD", "YYYY-M-DD", "MMMM D, YYYY", "YYYY‑MM‑DD"]
    for fmt in formats:
        try:
            date = arrow.get(date_str.strip(), fmt)
            break
        except Exception:
            date = arrow.now()

    return date


async def get_changelog() -> dict[str, Any]:
    platform = "ios"

    map_dict = {
        "ios": "iOS",
        "android": "Android",
        "cpp": "C++",
    }
    if platform.lower() not in map_dict:
        raise ValueError(f"Unsupported platform: {platform}")  # noqa: TRY003

    async with HTTPClient() as client:
        platform_in_url = platform.replace("-", "_")
        url = f"https://developers.google.com/admob/{platform_in_url}/rel-notes"
        html_text = (await client.get(url)).content.decode("utf-8")
        tree = html.fromstring(html_text)
        table = tree.xpath("//table")[0]

        items = []
        for row in table.xpath(".//tr"):
            if not row.xpath(".//td"):
                continue
            version = row.xpath(".//td")[0].text_content()
            date_str = row.xpath(".//td")[1].text_content().strip()
            note = row.xpath(".//td")[2].text_content()
            items.append(
                {
                    "title": f"AdMob SDK {map_dict[platform]} {version} Update",
                    "description": note,
                    "link": url,
                    "pub_date": get_date(date_str),
                }
            )

    return {
        "title": f"{plugin["pod"]} iOS Changelog",
        "link": url,
        "description": "Latest AdMob SDK update.",
        "pub_date": items[0]["pub_date"],
        "items": items,
    }


plugin = {"pod": "Google-Mobile-Ads-SDK", "provider": get_changelog}
