---
title: Karar (Kod, EV) — Otomatik .docx Sonuç Raporlama
tags: [karar, kod, ev, raporlama, çıktı-üretimi]
source: raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Karar (Kod, EV) — Otomatik .docx Sonuç Raporlama

## Karar

Her problem örneği için, konsol çıktısı `Tee` sınıfı (satır 31-41, hem stdout'a hem bir `io.StringIO()` tamponuna yazan basit bir çoklayıcı) ile yakalanıyor; çalışma sonunda `write_output_docx()` (satır 44-52, `python-docx` ile) bu log metnini `sonuclar/<KOD>.docx` olarak kaydediyor (satır 610-618, 775-778).

## Gerekçe / kanıt

Bu mekanizma, `raw/sonuclar/` klasöründeki `C5.docx`, `R5.docx`, `RC5.docx`, `C7.docx`, ... gibi dosyaların **doğrudan kaynağıdır** — bu dosyalar el ile yazılmış rapor değil, `EV_v.1.1.py`'nin çalıştırılmasının otomatik çıktısı. `Optimizasyon_Sonuclari_Birlesimi.docx` muhtemelen bu tekil dosyaların manuel olarak birleştirilmiş hali (bu ingest kapsamında doğrulanmadı — `raw/sonuclar/` henüz ingest edilmedi).

## Sources

- `raw/EV_v.1.1.py:31-52,610-618,775-778`

## Related

- [[sources/2026-08-09-ev_v1_1]]
- [[cozum_raporlama_fonksiyonlari]]
