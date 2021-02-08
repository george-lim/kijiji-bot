import os
from io import BytesIO
from pathlib import Path
from time import strftime
from zipfile import ZipFile

import requests
from kijiji_bot import KijijiBot, KijijiBotException

ads_url = os.environ["SCHEDULE_KIJIJI_ADS_URL"]
ssid = os.environ["SCHEDULE_KIJIJI_SSID"]

ads_path = Path("ads")

is_using_alternate_ads = int(strftime("%j")) % 2 == 0
post_delay_seconds = 0

response = requests.get(ads_url)
response.raise_for_status()

with ZipFile(BytesIO(response.content)) as archive:
    archive.extractall(ads_path)

try:
    bot = KijijiBot(ssid)
    bot.repost_ads(ads_path, is_using_alternate_ads, post_delay_seconds)
except KijijiBotException as exception:
    exception.dump()
    raise
