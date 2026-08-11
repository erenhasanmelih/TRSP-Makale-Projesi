"""TRSP projesi için günlük değişiklik özeti üretir (log.md + decisions/ taraması -> daily_summary.md)."""

import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
LOG_FILE = ROOT / "log.md"
DECISIONS_DIR = ROOT / "decisions"
OUTPUT_FILE = ROOT / "daily_summary.md"

LOG_ENTRY_RE = re.compile(
    r"^## \[(\d{4}-\d{2}-\d{2})\]\s+(\S+)\s*\|\s*(.+)$", re.MULTILINE
)


def get_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def parse_log_entries(today: str) -> list[dict]:
    if not LOG_FILE.exists():
        return []

    text = LOG_FILE.read_text(encoding="utf-8")
    matches = list(LOG_ENTRY_RE.finditer(text))
    entries = []

    for i, m in enumerate(matches):
        date, op_type, title = m.group(1), m.group(2), m.group(3).strip()
        if date != today:
            continue
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        entries.append({"date": date, "type": op_type, "title": title, "body": body})

    return entries


def extract_frontmatter_field(content: str, field: str) -> str:
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return ""
    field_match = re.search(rf"^{field}:\s*(.+)$", fm_match.group(1), re.MULTILINE)
    return field_match.group(1).strip() if field_match else ""


def find_todays_decisions(today: str) -> list[dict]:
    if not DECISIONS_DIR.exists():
        return []

    todays_decisions = []
    for path in sorted(DECISIONS_DIR.glob("*.md")):
        if path.name == ".gitkeep":
            continue

        content = path.read_text(encoding="utf-8")
        fm_date = extract_frontmatter_field(content, "date")
        mtime_date = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")

        if fm_date == today or mtime_date == today:
            title = extract_frontmatter_field(content, "title") or path.stem
            status = extract_frontmatter_field(content, "status") or "bilinmiyor"
            todays_decisions.append(
                {"path": f"decisions/{path.name}", "title": title, "status": status}
            )

    return todays_decisions


def render_summary(today: str, log_entries: list[dict], decisions: list[dict]) -> str:
    lines = [
        f"# TRSP Günlük Değişiklik Özeti — {today}",
        "",
        f"_Otomatik üretildi: `generate_report.py` | Tarih: {today}_",
        "",
    ]

    lines.append("## 📋 Bugünkü Log Kayıtları (`log.md`)")
    lines.append("")
    if log_entries:
        for e in log_entries:
            lines.append(f"### `{e['type']}` — {e['title']}")
            lines.append("")
            if e["body"]:
                lines.append(e["body"])
            lines.append("")
    else:
        lines.append("_Bugün `log.md`'ye yeni bir kayıt eklenmedi._")
        lines.append("")

    lines.append("## 📁 Bugün Eklenen/Güncellenen Karar Sayfaları (`decisions/`)")
    lines.append("")
    if decisions:
        lines.append("| Sayfa | Başlık | Durum |")
        lines.append("|---|---|---|")
        for d in decisions:
            lines.append(f"| `{d['path']}` | {d['title']} | {d['status']} |")
        lines.append("")
    else:
        lines.append("_Bugün `decisions/` klasöründe yeni/güncellenmiş sayfa yok._")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("_Bu rapor TRSP Proje Koordinatörü ajanı tarafından tetiklenmiştir._")

    return "\n".join(lines)


def main() -> None:
    today = get_today()
    log_entries = parse_log_entries(today)
    decisions = find_todays_decisions(today)

    summary = render_summary(today, log_entries, decisions)
    OUTPUT_FILE.write_text(summary, encoding="utf-8")

    print(f"[generate_report.py] {OUTPUT_FILE.name} uretildi ({today}).")
    print(f"[generate_report.py] {len(log_entries)} log kaydi, {len(decisions)} karar sayfasi bulundu.")


if __name__ == "__main__":
    main()
