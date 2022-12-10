import os
import json
import requests
import boto3
from io import StringIO
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


class Scraper:
    def __init__(self, hostname: str):
        self.hostname = hostname

    def products_url(self):
        return f"https://{self.hostname}/products.json"

    def fetch_json(self, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        try:
            data = json.loads(response.text)
        except err:
            raise SystemExit(err)

        return data

    def get_products(self):
        return self.fetch_json(self.products_url())


class NotificationAdapter:
    pass


class SlackNotificationAdapter(NotificationAdapter):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, message):
        slack_data = {"blocks": message}

        byte_length = str(os.sys.getsizeof(slack_data))
        headers = {"Content-Type": "application/json", "Content-Length": byte_length}
        response = requests.post(
            self.webhook_url, data=json.dumps(slack_data, indent=4), headers=headers
        )

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

    def notify(self, removed, new):
        self.send(self.format_message(removed, new))

    def format_html(self, html):
        return self.strip_tags(
            html.replace("<strong>", "*")
            .replace("</strong>", "*")
            .replace("<br>", "\n")
        )

    def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    def format_new(self, beer):
        url = f"https://www.bloodbrothersbrewing.com/collections/beer/products/{beer[1]['handle']}"
        title = beer[1]["title"]
        body = self.format_html(beer[1]["body_html"])

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{url}|{title}>*\n{body}",
                },
                "accessory": {
                    "type": "image",
                    "image_url": beer[1]["images"][0]["src"],
                    "alt_text": title,
                },
            },
            {"type": "divider"},
        ]

        return blocks

    def format_old(self, removed: tuple):
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Removed:* ~"
                    + ", ".join([beer[1]["title"] for beer in removed.items()])
                    + "~",
                },
            }
        ]

    def format_message(self, removed: dict, new: dict):
        new_count = len(new)
        new_plural = (
            f"are *{new_count} new* beers" if new_count != 1 else "is *1 new* beer"
        )
        old_count = len(removed)
        old_plural = "beers have" if old_count != 1 else "beer has"

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":beer: :drop_of_blood: *BLOOD BROTHERS BOTTLE SHOP UPDATE ALERT* :drop_of_blood: :beer:\n\nThere {new_plural} and *{old_count} old* {old_plural} been removed.",
                },
            },
            {"type": "divider"},
        ]
        for beer in new.items():
            blocks = blocks + self.format_new(beer)

        if old_count:
            blocks = blocks + self.format_old(removed)

        return blocks


class StateAdapter:
    def load(self):
        pass

    def save(self, state: dict):
        pass


class FileStateAdapter(StateAdapter):
    def __init__(self, filename):
        self.filename = filename

    def load(self):
        with open(self.filename) as state_file:
            file_contents = state_file.read()
            parsed_json = json.loads(file_contents)
            return parsed_json

    def save(self, state: dict):
        with open(self.filename, "w") as file:
            file.write(json.dumps(state, indent=4))


class S3StateAdapter(StateAdapter):
    def __init__(self, filename: str, bucket: str):
        self.filename = filename
        self.bucket = bucket
        self.client = boto3.client("s3")

    def load(self):
        data = self.client.get_object(Bucket=self.bucket, Key=self.filename)
        contents = data["Body"].read()
        parsed_json = json.loads(contents.decode("utf-8"))
        return parsed_json

    def save(self, state: dict):
        body = json.dumps(state, indent=4)
        self.client.put_object(Body=body, Bucket=self.bucket, Key=self.filename)


class App:
    def __init__(
        self,
        scraper: Scraper,
        filters: dict,
        fields: list,
        state_adapter: StateAdapter,
        notification_adapter: NotificationAdapter,
    ):
        self.scraper = scraper
        self.filters = filters
        self.fields = fields
        self.state_adapter = state_adapter
        self.notification_adapter = notification_adapter
        self.previous_state = self.state_adapter.load()

    def match_filters(self, element):
        for key, match in self.filters.items():
            if element[key].lower() != match.lower():
                return False

        return True

    def format_element(self, element):
        return {key: element[key] for key in element.keys() & self.fields}

    def check_for_update(self):
        products = self.scraper.get_products()
        matches = {
            str(element["id"]): self.format_element(element)
            for element in products["products"]
            if self.match_filters(element)
        }

        removed = {
            k: v
            for k, v in self.previous_state.items()
            if k in set(self.previous_state.keys()) - set(matches.keys())
        }
        new = {
            k: v
            for k, v in matches.items()
            if k in set(matches.keys()) - set(self.previous_state.keys())
        }

        if len(removed) > 0 or len(new) > 0:
            self.notification_adapter.notify(removed, new)
            self.state_adapter.save(matches)
