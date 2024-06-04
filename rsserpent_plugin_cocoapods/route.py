import hashlib
from typing import Any

import feedparser
from starlette.exceptions import HTTPException

from rsserpent_rev.utils import cached

from .github_release import get_changelog, get_changelog_by_url
from feedgen.feed import FeedGenerator

from feedparser_to_feedgen import to_feedgen

import rsserpent_plugin_admob_sdk_update
import rsserpent_plugin_applovin_sdk_update
import rsserpent_plugin_csj_sdk_update

path = "/cocoapods/{pod}"


@cached
async def provider(pod: str) -> dict[str, Any]:
    if pod == "AppLovinSDK":
        return await rsserpent_plugin_applovin_sdk_update.route.provider("ios")
    if pod == "Google-Mobile-Ads-SDK":
        return await rsserpent_plugin_admob_sdk_update.route.provider("ios")
    if pod == "Ads-CN-Beta":
        return await rsserpent_plugin_csj_sdk_update.route.provider(148)
    if pod == "Alamofire":
        return get_changelog_by_url("https://github.com/Alamofire/Alamofire")

    github_release_note = await get_changelog(pod)
    if github_release_note:
        github_release_note.title(f"{pod} Changelog")
        return github_release_note

    return await get_specs_log(pod)

async def get_specs_log(pod: str) -> FeedGenerator:
    md5 = hashlib.md5(pod.encode()).hexdigest()
    commit_atom = f"https://github.com/CocoaPods/Specs/commits/master/Specs/{md5[0]}/{md5[1]}/{md5[2]}/{pod}.atom"
    feed = feedparser.parse(commit_atom)
    if not feed.entries:
        raise HTTPException(
            status_code=404, detail="Pod not found, please check the pod name, and the name is case-sensitive."
        )

    changelog_url = {
        "Google-Mobile-Ads-SDK": "https://developers.google.com/admob/ios/rel-notes",
        "AppLovinSDK": "https://developers.applovin.com/en/ios/changelog",
        "Firebase": "https://firebase.google.com/support/release-notes/ios",
        "FacebookSDK": "https://github.com/facebook/facebook-ios-sdk/blob/main/CHANGELOG.md",
        "Ads-CN": "https://www.csjplatform.com/supportcenter/5373",
        "Ads-Gloabl": "https://www.csjplatform.com/supportcenter/5373",
        "AppsFlyerFramework": "https://support.appsflyer.com/hc/en-us/articles/115001224823-AppsFlyer-iOS-SDK-release-notes",
    }

    fg = to_feedgen(feed)
    fg.title(f"{pod} Changelog")

    for entry in fg.entry():
        entry.description(entry.description() + f"\nChangelog: {changelog_url.get(pod, '')}" if pod in changelog_url else "")

    return fg
