class NotificationService:
    async def send_email(self, *, to_email: str, subject: str, body: str) -> None:
        # Integration hook: existing Django SMTP/email flow remains unchanged.
        _ = (to_email, subject, body)
