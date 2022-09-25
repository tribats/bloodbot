import os
from bloodbot.bloodbot import *


def main(event, context):
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    state_adapter = S3StateAdapter("state.json", os.getenv("STATE_BUCKET"))
    notification_adapter = SlackNotificationAdapter(
        webhook_url=slack_webhook_url
    )

    app = App(
        scraper=Scraper(hostname="www.bloodbrothersbrewing.com"),
        filters={"product_type": "beer"},
        fields=["title", "published_at", "images", "body_html", "handle"],
        state_adapter=state_adapter,
        notification_adapter=notification_adapter,
    )

    app.check_for_update()
