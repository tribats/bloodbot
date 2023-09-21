import os
from bloodbot.bloodbot import *


def main(event={}, context={}):
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    notification_adapter = SlackNotificationAdapter(webhook_url=slack_webhook_url)

    breweries = [
        Brewery(
            scraper=ShopifyScraper(
                products_url="https://kensington-brewing.myshopify.com/collections/local-craft-beer/products.json"
            ),
            filters={},
            fields=["title", "published_at", "images", "body_html", "handle"],
            state_adapter=S3StateAdapter(
                "kensington-brewing.myshopify.com.json", os.getenv("STATE_BUCKET")
            ),
            notification_adapter=notification_adapter,
            header="Kensington Brewing",
            link_template="https://kensington-brewing.myshopify.com/collections/local-craft-beer/products/{handle}",
        ),
        Brewery(
            scraper=ShopifyScraper(
                products_url="https://indiealehouse.com/collections/online-bottle-shop/products.json"
            ),
            filters={},
            fields=["title", "published_at", "images", "body_html", "handle"],
            state_adapter=S3StateAdapter(
                "indiealehouse.com.json", os.getenv("STATE_BUCKET")
            ),
            notification_adapter=notification_adapter,
            header="Indie Ale House",
            link_template="https://indiealehouse.com/collections/online-bottle-shop/products/{handle}",
        ),
        Brewery(
            scraper=ShopifyScraper(
                products_url="https://shortfingerbrewing.com/collections/sfbc-bottle-shop-online/products.json"
            ),
            filters={},
            fields=["title", "published_at", "images", "body_html", "handle"],
            state_adapter=S3StateAdapter(
                "shortfingerbrewing.com.json", os.getenv("STATE_BUCKET")
            ),
            notification_adapter=notification_adapter,
            header="Short Finger",
            link_template="https://shortfingerbrewing.com/collections/sfbc-bottle-shop-online/products/{handle}",
        ),
        Brewery(
            scraper=ShopifyScraper(
                products_url="https://bellwoodsbrewery.com/collections/beer/products.json"
            ),
            filters={"product_type": ["beer"]},
            fields=["title", "published_at", "images", "body_html", "handle"],
            state_adapter=S3StateAdapter(
                "bellwoodsbrewery.com.json", os.getenv("STATE_BUCKET")
            ),
            notification_adapter=notification_adapter,
            header="Bellwoods",
            link_template="https://bellwoodsbrewery.com/collections/beer/products/{handle}",
        ),
        Brewery(
            scraper=ShopifyScraper(
                products_url="https://fanshop.leftfieldbrewery.ca/collections/beer/products.json"
            ),
            filters={"product_type": ["misc", "packaged"]},
            fields=["title", "published_at", "images", "body_html", "handle"],
            state_adapter=S3StateAdapter(
                "leftfieldbrewery.ca.json", os.getenv("STATE_BUCKET")
            ),
            notification_adapter=notification_adapter,
            header="Left Field",
            link_template="https://fanshop.leftfieldbrewery.ca/collections/beer/products/{handle}",
        ),
        Brewery(
            scraper=ShopifyScraper(
                products_url="https://burdockbrewery.com/collections/beer/products.json"
            ),
            filters={"product_type": ["beer"]},
            fields=["title", "published_at", "images", "body_html", "handle"],
            state_adapter=S3StateAdapter(
                "burdockbrewery.com.json", os.getenv("STATE_BUCKET")
            ),
            notification_adapter=notification_adapter,
            header="Burdock",
            link_template="https://burdockbrewery.com/collections/beer/products/{handle}",
        ),
        Brewery(
            scraper=ShopifyScraper(
                products_url="https://collectiveartsontario.com/products.json"
            ),
            filters={"product_type": ["beer", "spirits & cocktails", "beer & cider"]},
            fields=["title", "published_at", "images", "body_html", "handle"],
            state_adapter=S3StateAdapter(
                "collectiveartsontario.com.json", os.getenv("STATE_BUCKET")
            ),
            notification_adapter=notification_adapter,
            header="Collective Arts",
            link_template="https://collectiveartsontario.com/collections/beer/products/{handle}",
        ),
        Brewery(
            scraper=ShopifyScraper(
                products_url="https://www.bloodbrothersbrewing.com/collections/beer/products.json"
            ),
            filters={"product_type": ["beer"]},
            fields=["title", "published_at", "images", "body_html", "handle"],
            state_adapter=S3StateAdapter(
                "bloodbrothersbrewing.com.json", os.getenv("STATE_BUCKET")
            ),
            notification_adapter=notification_adapter,
            header=":drop_of_blood: Blood Brothers",
            link_template="https://www.bloodbrothersbrewing.com/collections/beer/products/{handle}",
        ),
        Brewery(
            scraper=ShopifyScraper(
                products_url="https://slakebrewing.com/collections/beer/products.json"
            ),
            filters={"product_type": ["Beer"]},
            fields=["title", "published_at", "images", "body_html", "handle"],
            state_adapter=S3StateAdapter(
                "slakebrewing.com.json", os.getenv("STATE_BUCKET")
            ),
            notification_adapter=notification_adapter,
            header="Slake",
            link_template="https://slakebrewing.com/collections/beer/products/{handle}",
        ),
    ]

    for brewery in breweries:
        brewery.check_for_update()
