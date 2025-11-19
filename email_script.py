import argparse
import os
import sys
import getpass
import mimetypes
import ssl
import smtplib
import logging
from email.message import EmailMessage
from typing import List

"""
main.py - simple email sender script

Features:
- Send plain text or HTML emails
- Attach files
- Multiple recipients (comma-separated or repeated -t)
- Read SMTP credentials from environment (EMAIL_USERNAME, EMAIL_PASSWORD) or prompt for password
- TLS support
- Optional attachment MIME detection
- Basic error handling and logging

Usage examples:
    python main.py -s "Test" -b "Hello" -t alice@example.com -f /path/to/file.pdf
    python main.py --subject "Hi" --body-file body.html --html --to alice@example.com,bob@example.com
"""


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def build_message(
        subject: str,
        body: str,
        sender: str,
        recipients: List[str],
        html: bool = False,
        attachments: List[str] = [],
) -> EmailMessage:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)

        if html:
                # set a plain fallback and HTML alternative
                msg.set_content("This is an HTML email. Your client does not support HTML display.")
                msg.add_alternative(body, subtype="html")
        else:
                msg.set_content(body)

        attachments = attachments or []
        for path in attachments:
                if not os.path.isfile(path):
                        logging.warning("Attachment not found and will be skipped: %s", path)
                        continue
                ctype, encoding = mimetypes.guess_type(path)
                if ctype is None:
                        ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)
                with open(path, "rb") as f:
                        data = f.read()
                msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(path))

        return msg


def send_email(
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        msg: EmailMessage,
        use_tls: bool = True,
        use_ssl: bool = False,
) -> None:
        if use_ssl:
                context = ssl.create_default_context()
                logging.info("Connecting to %s:%s using SSL", smtp_host, smtp_port)
                with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                        server.login(username, password)
                        server.send_message(msg)
        else:
                logging.info("Connecting to %s:%s", smtp_host, smtp_port)
                with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                        server.ehlo()
                        if use_tls:
                                context = ssl.create_default_context()
                                server.starttls(context=context)
                                server.ehlo()
                        if username:
                                server.login(username, password)
                        server.send_message(msg)
        logging.info("Email sent to: %s", msg["To"])


def parse_recipients(recipients: List[str]) -> List[str]:
        out = []
        for r in recipients:
                parts = [x.strip() for x in r.replace(";", ",").split(",")]
                out.extend([p for p in parts if p])
        return out


def read_file_or_die(path: str) -> str:
        if not path:
                return ""
        if not os.path.isfile(path):
                logging.error("File not found: %s", path)
                sys.exit(2)
        with open(path, "r", encoding="utf-8") as f:
                return f.read()


def main():
        parser = argparse.ArgumentParser(description="Send an email via SMTP.")
        parser.add_argument("--smtp-host", default=os.environ.get("SMTP_HOST", "smtp.gmail.com"), help="SMTP server host")
        parser.add_argument("--smtp-port", type=int, default=int(os.environ.get("SMTP_PORT", 587)), help="SMTP server port")
        parser.add_argument("--ssl", action="store_true", help="Use SSL (SMTP_SSL) instead of STARTTLS")
        parser.add_argument("--no-tls", dest="tls", action="store_false", help="Disable STARTTLS (if not using SSL)")
        parser.add_argument("-u", "--username", default=os.environ.get("EMAIL_USERNAME"), help="SMTP username (also used as From if --from is not set)")
        parser.add_argument("-p", "--password", help="SMTP password (if not provided will read EMAIL_PASSWORD or prompt)")
        parser.add_argument("--from", dest="from_addr", help="From email address (defaults to username)")
        parser.add_argument("-t", "--to", action="append", required=True, help="Recipient address (can be repeated or comma-separated)")
        parser.add_argument("-s", "--subject", default="(no subject)", help="Email subject")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-b", "--body", help="Email body text")
        group.add_argument("--body-file", help="Read email body from file")
        parser.add_argument("--html", action="store_true", help="Send body as HTML (uses --body or --body-file)")
        parser.add_argument("-a", "--attach", action="append", help="Attach files (can be repeated)")
        parser.add_argument("--dry-run", action="store_true", help="Build message and print but do not send")
        args = parser.parse_args()

        recipients = parse_recipients(args.to)
        if not recipients:
                logging.error("No recipients provided")
                sys.exit(2)

        sender = args.from_addr or args.username
        if not sender:
                logging.error("From address not provided and username not set")
                sys.exit(2)

        body = args.body or read_file_or_die(args.body_file) or ""
        password = args.password or os.environ.get("EMAIL_PASSWORD")
        if args.username and not password:
                # prompt securely if needed
                password = getpass.getpass(prompt=f"Password for {args.username}: ")

        msg = build_message(
                subject=args.subject,
                body=body,
                sender=sender,
                recipients=recipients,
                html=args.html,
                attachments=args.attach,
        )

        if args.dry_run:
                print("DRY RUN - message preview:\n")
                print(msg)
                return

        try:
                send_email(
                        smtp_host=args.smtp_host,
                        smtp_port=args.smtp_port,
                        username=args.username or "",
                        password=password or "",
                        msg=msg,
                        use_tls=args.tls,
                        use_ssl=args.ssl,
                )
        except Exception as e:
                logging.error("Failed to send email: %s", e)
                sys.exit(1)


if __name__ == "__main__":
        main()