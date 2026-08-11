"""daily_summary.md icerigini SMTP uzerinden ekip uyelerine e-posta olarak gonderir.

--dry-run ile calistirildiginda e-posta gonderilmez, sadece taslak (Kimden/Kime/Konu/Govde)
ekrana yazdirilir. Bu, gondermeden once onay almak icin kullanilir.
"""

import argparse
import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
SUMMARY_FILE = ROOT / "daily_summary.md"

RECIPIENTS = [
    "melihusllu@gmail.com",
    "hasancolak1298@gmail.com",
    "erennbsn@gmail.com",
]


def load_config() -> dict:
    load_dotenv(ROOT / ".env")

    config = {
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("SMTP_USERNAME"),
        "password": os.getenv("SMTP_PASSWORD"),
        "sender_name": os.getenv("SENDER_NAME", "TRSP Proje Botu"),
    }

    missing = [k for k in ("username", "password") if not config[k]]
    if missing:
        raise RuntimeError(
            "Eksik .env degiskeni: "
            + ", ".join(f"SMTP_{m.upper()}" for m in missing)
            + " — lutfen .env.example dosyasini .env olarak kopyalayip doldurun."
        )

    return config


def build_message(config: dict, body: str, today: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"TRSP Gunluk Degisiklik Ozeti - {today}"
    msg["From"] = f"{config['sender_name']} <{config['username']}>"
    msg["To"] = ", ".join(RECIPIENTS)
    msg.attach(MIMEText(body, "plain", "utf-8"))
    return msg


def send(config: dict, msg: MIMEMultipart) -> None:
    with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
        server.starttls()
        server.login(config["username"], config["password"])
        server.sendmail(config["username"], RECIPIENTS, msg.as_string())


def print_preview(config: dict, body: str, today: str) -> None:
    print("==================== E-POSTA TASLAGI (henuz GONDERILMEDI) ====================")
    print(f"Kimden : {config['sender_name']} <{config['username']}>")
    print(f"Kime   : {', '.join(RECIPIENTS)}")
    print(f"Konu   : TRSP Gunluk Degisiklik Ozeti - {today}")
    print("--------------------------------------------------------------------------------")
    print(body)
    print("================================================================================")
    print("[send_mail.py] Bu bir ON IZLEME'dir, e-posta gonderilmedi. Onay sonrasi '--dry-run' olmadan calistirin.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="daily_summary.md'yi ekibe e-posta olarak gonderir.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="E-postayi gondermeden taslagini (Kimden/Kime/Konu/Govde) ekrana yazdirir.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not SUMMARY_FILE.exists():
        print(f"[send_mail.py] HATA: {SUMMARY_FILE.name} bulunamadi. Once generate_report.py calistirin.")
        sys.exit(1)

    body = SUMMARY_FILE.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        config = load_config()
    except RuntimeError as exc:
        print(f"[send_mail.py] HATA: {exc}")
        sys.exit(1)

    if args.dry_run:
        print_preview(config, body, today)
        return

    msg = build_message(config, body, today)

    try:
        send(config, msg)
    except smtplib.SMTPAuthenticationError:
        print(
            "[send_mail.py] HATA: SMTP kimlik dogrulama basarisiz. "
            "Gmail kullaniyorsaniz normal sifre degil, 'Uygulama Sifresi' (App Password) gerekir."
        )
        sys.exit(1)
    except Exception as exc:
        print(f"[send_mail.py] HATA: e-posta gonderilemedi -> {exc}")
        sys.exit(1)

    print(f"[send_mail.py] Rapor {len(RECIPIENTS)} aliciya gonderildi: {', '.join(RECIPIENTS)}")


if __name__ == "__main__":
    main()
