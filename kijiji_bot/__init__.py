import logging
from functools import reduce
from pathlib import Path
from time import sleep, strftime

import yaml
from kijiji_bot import kijiji_api
from requests.utils import add_dict_to_cookiejar


class KijijiBotException(Exception):
    def __init__(self, message="Kijiji Bot exception encountered.", html_dump=None):
        self.ad_title = "Unknown Ad Title"
        self.message = message
        self.html_dump_filename = f"kijiji_bot_dump_{strftime('%Y%m%dT%H%M%S')}.html"
        self.html_dump = html_dump

    def __str__(self):
        message_prefix = f"{self.ad_title}:\n" if self.ad_title else ""

        message_suffix = (
            f" (dump available)\n{self.html_dump_filename}" if self.html_dump else ""
        )

        return f"{message_prefix}{self.message}{message_suffix}"

    def dump(self, path_str="."):
        if self.html_dump:
            html_dump_path = Path(path_str).joinpath(self.html_dump_filename)
            html_dump_path.parent.mkdir(0o755, True, True)
            html_dump_path.write_text(self.html_dump)


class KijijiBotRepostException(KijijiBotException):
    def __init__(self, exceptions):
        self.exceptions = exceptions

    def __str__(self):
        return "\n\n".join(map(str, self.exceptions))

    def dump(self, path_str="."):
        [exception.dump() for exception in self.exceptions]


# Overwrite default API exception
kijiji_api.KijijiApiException = KijijiBotException


class KijijiBot(kijiji_api.KijijiApi):
    def __init__(self, ssid):
        super().__init__()

        logging.info("Logging in with SSID cookie value...")
        add_dict_to_cookiejar(self.session.cookies, {"ssid": ssid})

        if not self.is_logged_in():
            raise KijijiBotException("authentication failed")

    def get_ad_file_paths(self, path):
        if path.is_file():
            return [path] if path.suffix == ".yml" or path.suffix == ".yaml" else []

        return reduce(lambda x, y: x + self.get_ad_file_paths(y), path.iterdir(), [])

    def repost_ads(self, ads_path, is_using_alternate_ads=False, post_delay_seconds=30):
        logging.info("Deleting ads...")
        [self.delete_ad(ad["id"]) for ad in self.get_all_ads()]

        exceptions = []

        for ad_file_path in self.get_ad_file_paths(ads_path):
            ad_data = yaml.load(ad_file_path.read_text(), yaml.FullLoader)

            ad_images = [
                ad_file_path.with_name(image_path).read_bytes()
                for image_path in ad_data["image_paths"]
            ]

            del ad_data["image_paths"]

            if is_using_alternate_ads:
                ad_data["postAdForm.title"] = ad_data.get(
                    "postAdForm.alternateTitle", ad_data["postAdForm.title"]
                ).strip()

                ad_data["postAdForm.city"] = ad_data.get(
                    "postAdForm.alternateCity", ad_data["postAdForm.city"]
                )

                ad_data["postAdForm.addressCity"] = ad_data.get(
                    "postAdForm.alternateAddressCity", ad_data["postAdForm.addressCity"]
                )

                ad_data["postAdForm.description"] = ad_data.get(
                    "postAdForm.alternateDescription", ad_data["postAdForm.description"]
                )
            else:
                ad_data["postAdForm.title"] = ad_data["postAdForm.title"].strip()

            ad_title = ad_data["postAdForm.title"]

            try:
                logging.info(f"Posting ad: {ad_title}")
                self.post_ad_using_data(ad_data, ad_images)

                if post_delay_seconds == 0:
                    sleep(post_delay_seconds)

                    all_ads = self.get_all_ads()

                    is_active_ad = [
                        ad["title"] for ad in all_ads if ad["title"] == ad_title
                    ]

                    if not is_active_ad:
                        raise KijijiBotException("duplicate ad removed by Kijiji")
            except KijijiBotException as exception:
                logging.warn(f"Failed to post ad: {ad_title}")
                exception.ad_title = ad_title
                exceptions.append(exception)

        if exceptions:
            raise KijijiBotRepostException(exceptions)
