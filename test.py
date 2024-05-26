import base64


email_recipient = "me"
mail_subject = "you"
mail_body = "subject"


message = {
        'raw': base64.urlsafe_b64encode(
            f'MIME-Version: 1.0\n'
            f'Content-Type: text/html; charset="UTF-8"\n'
            f"From: itbase.tv@gmail.com\n"
            f"To: {email_recipient}\n"
            f"Subject: {mail_subject}\n\n"
            f"{mail_body}"
            .encode("utf-8")
        ).decode("utf-8")
    }