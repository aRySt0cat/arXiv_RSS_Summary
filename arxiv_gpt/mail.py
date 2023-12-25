import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv


def create_message(
    title: str, content: str, from_address: str, to_address: str
) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = title
    message["From"] = from_address
    message["To"] = to_address
    message.set_content(content, subtype="html")

    return message


def send_mail(
    title: str,
    content: str,
    login_address: str,
    login_password: str,
    address_list: list[str],
    smtp_server: str = "smtp.gmail.com",
    port: int = 465,
):
    context = smtplib.ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as smtp:
        smtp.login(login_address, login_password)
        for address in address_list:
            message = create_message(title, content, login_address, address)
            smtp.send_message(message)