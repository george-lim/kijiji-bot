from pathlib import Path

from kijiji_bot import KijijiBot, KijijiBotException

ssid = ""
ads_path = Path("ads")
is_using_alternate_ads = False
post_delay_seconds = 0

try:
    bot = KijijiBot(ssid)
    bot.repost_ads(ads_path, is_using_alternate_ads, post_delay_seconds)
except KijijiBotException as exception:
    exception.dump()
    raise
