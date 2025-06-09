from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_confirmation_email(user_email: str, code: str):
    subject = "Подтверждение входа"
    html_template = render_to_string(
        template_name="email_template/confirm_code.html",
        context={
            "code": code,
            "valid_minutes": 5,
        },
    )
    email = EmailMessage(
        subject=subject,
        body=html_template,
        from_email="manager@skazka-design.ru",
        to=[user_email],
    )
    email.content_subtype = "html"
    email.send()
