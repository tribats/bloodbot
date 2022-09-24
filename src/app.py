import bloodbot

def main():
    slack_webhook_url = os.getenv(
        "SLACK_WEBHOOK_URL",
    )
    state_adapter = FileStateAdapter("state.json")
    notification_adapter = SlackNotificationAdapter(webhook_url=slack_webhook_url)

    app = App(
        scraper=Scraper(hostname="www.bloodbrothersbrewing.com"),
        filters={"product_type": "beer"},
        fields=["title", "published_at", "images", "body_html", "handle"],
        state_adapter=state_adapter,
        notification_adapter=notification_adapter,
    )

    app.check_for_update()

