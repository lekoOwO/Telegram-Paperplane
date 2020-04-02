from userbot import CMD_HELP
from userbot.events import register
import requests
from lxml.html import fromstring

def __title(url):
    r = requests.get(url)
    tree = fromstring(r.content)
    title = tree.findtext('.//title')

@register(outgoing=True, pattern="^.link(?: |$)(.*)")
async def weather(bot):
    if not bot.pattern_match.group(1):
        await bot.edit("`Please insert a URL.`")
    else:
        url = bot.pattern_match.group(1)

    await bot.edit(f"[{__title(url)}]({url})")

CMD_HELP.update({
    "link": ".link <URL>\n"
               "Usage: Convert a URL to a markdown hyperlink."
})
