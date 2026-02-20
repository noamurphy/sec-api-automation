from __future__ import annotations

from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .sec_client import SecClient


PDF_MAGIC = b"%PDF"


def _write_text_pdf(text: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    y = height - 40
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        chunks = [line[i : i + 110] for i in range(0, len(line), 110)]
        for chunk in chunks:
            pdf.drawString(40, y, chunk)
            y -= 14
            if y < 40:
                pdf.showPage()
                y = height - 40
    pdf.save()


def _html_to_text(html_bytes: bytes) -> str:
    soup = BeautifulSoup(html_bytes, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text("\n", strip=True)


def normalize_to_pdf(raw_bytes: bytes, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if raw_bytes.startswith(PDF_MAGIC):
        output_path.write_bytes(raw_bytes)
        return

    text = _html_to_text(raw_bytes)
    if not text:
        text = "Document downloaded but no readable text was extracted."
    _write_text_pdf(text, output_path)


def download_and_convert(
    sec: SecClient,
    source_url: str,
    output_path: Path,
) -> Path:
    payload = sec.get_bytes(source_url)
    normalize_to_pdf(payload, output_path)
    return output_path


def download_optional(
    sec: SecClient,
    source_url: Optional[str],
    output_path: Path,
) -> Path | None:
    if not source_url:
        return None
    return download_and_convert(sec, source_url, output_path)
