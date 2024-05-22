from typing import Any, Dict

import arrow
from rsserpent.utils import cached
import feedparser
from starlette.exceptions import HTTPException
import hashlib

from . import plugins

path = "/cocoapods/{pod}"

# get all plugins under current module's submodule named "plugins"
def get_plugins():
    import importlib
    import pkgutil

    _plugins = []
    for _, name, _ in pkgutil.iter_modules(plugins.__path__):
        module = importlib.import_module(f"{plugins.__name__}.{name}")
        if hasattr(module, "plugin"):
            _plugins.append(module)

    return _plugins

@cached
async def provider(pod: str) -> Dict[str, Any]:
    first = list(filter(lambda x: x.plugin['pod'] == pod, get_plugins()))
    if first:
        if 'github' in first[0].plugin:
            notes = plugins.github_release.get_changelog_by_url(first[0].plugin["github"])
            if notes:
                return notes
        return await first[0].plugin["provider"]()

    github_release_note = await plugins.github_release.get_changelog(pod)
    if github_release_note:
        return github_release_note

    md5 = hashlib.md5(pod.encode()).hexdigest()
    commit_atom = f"https://github.com/CocoaPods/Specs/commits/master/Specs/{md5[0]}/{md5[1]}/{md5[2]}/{pod}.atom"
    feed = feedparser.parse(commit_atom)
    if not feed.entries:
        raise HTTPException(status_code=404, detail="Pod not found")

    changelog_url = {
        "Google-Mobile-Ads-SDK": "https://developers.google.com/admob/ios/rel-notes",
        "AppLovinSDK": "https://developers.applovin.com/en/ios/changelog",
        "Firebase": "https://firebase.google.com/support/release-notes/ios",
        "FacebookSDK": "https://github.com/facebook/facebook-ios-sdk/blob/main/CHANGELOG.md",
        "Ads-CN": "https://www.csjplatform.com/supportcenter/5373",
        "Ads-Gloabl": "https://www.csjplatform.com/supportcenter/5373",
        "AppsFlyerFramework": "https://support.appsflyer.com/hc/en-us/articles/115001224823-AppsFlyer-iOS-SDK-release-notes",
    }

    return {
        "title": f"{pod} Changelog",
        "link": feed.feed.link,
        "description": feed.feed.title,
        "items": list(map(lambda x: {
            "title": x.title,
            "description": x.title + ("\n" + f"Changelog: {changelog_url.get(pod, '')}" if pod in changelog_url else ""),
            "link": x.link,
            "pub_date": arrow.get(x.updated),
        }, feed.entries))
    }
