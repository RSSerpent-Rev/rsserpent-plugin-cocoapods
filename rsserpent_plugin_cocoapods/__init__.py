from rsserpent_rev.models import Persona, Plugin

from . import route


plugin = Plugin(
    name="rsserpent-plugin-cocoapods",
    author=Persona(
        name="EkkoG",
        link="https://github.com/EkkoG",
        email="beijiu572@gmail.com",
    ),
    prefix="/cocoapods",
    repository="https://github.com/RSSerpent-Rev/rsserpent-plugin-cocoapods",
    routers={route.path: route.provider},
)
