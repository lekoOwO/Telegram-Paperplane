import weathercom
from json import loads
from userbot import CMD_HELP
from userbot.events import register

async def __weather(city):
    data = weathercom.getCityWeatherDetails(city)
    return loads(data)

async def __fetch(city):
    try:
        data = await __weather(city)

        text = f"**Temperature:** `{data['vt1observation']['temperature']}°C`\n" \
            + f"**Max. Temp:** `{data['vt1observation']['temperatureMaxSince7am']}°C`\n" \
            + f"**Appr. Temp:** `{data['vt1observation']['feelsLike']}°C`\n" \
            + f"**Humidity:** `{data['vt1observation']['humidity']}%`\n" \
            + f"**Wind:** `{data['vt1observation']['windSpeed']} kmh, {data['vt1observation']['windDirCompass']}({data['vt1observation']['windDirDegrees']}°)`\n" \
            + f"**UV:** `{data['vt1observation']['uvDescription']} ({data['vt1observation']['uvIndex']})`\n" \
            + f"**Visibility:** `{data['vt1observation']['visibility']} km`\n" \
            + f"\n\n**{data['vt1observation']['phrase']}\n**" \
            + f"`{data['city']}`\n" + f"`{data['vt1observation']['observationTime']}`"

        return text
    except:
        return "Location not found."

@register(outgoing=True, pattern="^.weather.com(?: |$)(.*)")
async def weather(bot):
    if not bot.pattern_match.group(1):
        await bot.edit("`Please specify a location.`")
    else:
        location = bot.pattern_match.group(1)

    await bot.edit(await __fetch(location))

CMD_HELP.update({
    "weather.com": ".weather.com <city> or .weather.com <city>, <country name/code>\n"
               "Usage: Gets the weather of a city."
})


