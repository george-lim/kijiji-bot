# Kijiji Bot

[![pypi](https://img.shields.io/pypi/v/kijiji-bot)](https://pypi.org/project/kijiji-bot)
![pyversions](https://img.shields.io/pypi/pyversions/kijiji-bot)
[![ci](https://github.com/george-lim/kijiji-bot/workflows/CI/badge.svg)](https://github.com/george-lim/kijiji-bot/actions)
[![license](https://img.shields.io/github/license/george-lim/kijiji-bot)](https://github.com/george-lim/kijiji-bot/blob/main/LICENSE)

## [Usage](#usage) | [Features](#features) | [Examples](#examples) | [CI/CD](#cicd)

Kijiji Bot is a Python library to repost ads on Kijiji with the Kijiji API.
The API is provided by [Kijiji-Repost-Headless](https://github.com/ArthurG/Kijiji-Repost-Headless).

## Usage

```bash
python3 -m pip install kijiji-bot
```

This installs Kijiji Bot and its dependencies. Once installed, add `import kijiji_bot` to a Python script to begin using Kijiji Bot.

> Note: you will need to create your ads with [Kijiji-Repost-Headless](https://github.com/ArthurG/Kijiji-Repost-Headless) first before using Kijiji Bot. Kijiji Bot will scan for ads in a specified root folder.

## Features

Kijiji Bot accepts a SSID cookie value to authenticate the user. To get this value:

1. Log into Kijiji on any browser, with `Keep me signed in` checked
2. Using a web inspector, copy the value of the `ssid` cookie in the domain `www.kijiji.ca`

Ensure that you do not log out of the Kijiji session afterwards. If you do, you will need another SSID cookie value to authenticate again.

### Multi-ad Reposting

Kijiji Bot will recursively find all ads in a specified root folder. The following is a valid folder structure for ads:

```text
ads
├── test_ad_1
│   ├── item.yaml
│   └── 1.JPG
└── test_ad_2
    ├── item.yaml
    └── 1.JPG
```

### Duplicate Ad Checking

Kijiji automatically deletes newly posted ads if they appear to be duplicates of existing ads. With the `post_delay_seconds` parameter, users can specify how long the bot waits before checking for duplicate ads. The default value is thirty seconds. Duplicate ad checking can be disabled entirely if the value is set to zero.

### Alternate Ad Support

With the `is_using_alternate_ad` flag, users can specify whether they want to repost ads using alternate details. This greatly reduces the chances of having reposted ads removed by Kijiji.

Add the following four fields to your ad's `item.yaml` file to specify alternate ad details:

```yaml
postAdForm.alternateTitle: Alternate ad title
postAdForm.alternateCity: New York
postAdForm.alternateAddressCity: New York
postAdForm.alternateDescription: Alternate ad description
```

## Examples

### Repost ads

This snippet logs into Kijiji and reposts ads.

```python
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
```

## CI/CD

### Secrets

```yaml
PYPI_USERNAME: __token__
PYPI_PASSWORD: "********"

TESTPYPI_USERNAME: __token__
TESTPYPI_PASSWORD: "********"
```

These secrets must exist in the repository for `CD` workflows to publish the PyPI package.

```yaml
SCHEDULE_KIJIJI_ADS_URL: https://...
SCHEDULE_KIJIJI_SSID: MTAyMDk5OTE1Mnxl...
```

These secrets must exist in the repository for `Schedule` workflow to periodically repost ads.
