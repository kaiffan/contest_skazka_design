from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_confirmation_email(user_email: str, code: str):
    subject = "Подтверждение входа"
    message = render_to_string(
        template_name="email_template/confirm_code.html",
        context={
            "code": code,
            "valid_minutes": 10,
        },
    )
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email="manager@skazka-design.ru",
        to=[user_email],
    )
    email.content_subtype = "html"  # для HTML-писем
    email.send()
