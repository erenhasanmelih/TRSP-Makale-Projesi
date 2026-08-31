---
title: format_time() Fonksiyonu
tags: [entity, fonksiyon, raporlama, zaman-formatı]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# format_time() Fonksiyonu

CV (`CV_model_gurobi_exact.py:200-207`) ve EV (`EV_v.1.1.py:384-391`) dosyalarında birebir aynı (kopya) fonksiyon. Saniye cinsinden bir model zamanını (`0` = gün başlangıcı) `HH:MM` formatında okunabilir saate çevirir:

```python
def format_time(seconds: float) -> str:
    if seconds is None:
        return "--:--"
    seconds = max(0, round(seconds))
    shifted_seconds = seconds + 28800   # +8 saat = 08:00 referans
    h = (shifted_seconds // 3600) % 24
    m = (shifted_seconds % 3600) // 60
    return f"{h:02d}:{m:02d}"
```

`+28800` (8 saat) kayması, modelin 0. saniyesinin operasyonel olarak sabah 08:00'e karşılık geldiği varsayımını kodluyor — bkz. [[karar_operasyonel_zaman_kaydirma_format_time]].

## Güncelleme (2026-08-22) — mantık aynı, satır numaraları değişti

`raw/CV_model_gurobi_exact.py`/`raw/EV_v.1.1.py`'nin 2026-08-22 yeniden yazımında `format_time()` **birebir aynı** (satır satır kod değişmedi), yalnızca dosya içindeki konumu kaydı: CV `419-426`, EV `369-376`. `+28800` kayması ve yorumlar aynen korunmuş.

## Sources

- `raw/CV_model_gurobi_exact.py:200-207` (eski, 2026-08-09 hâli)
- `raw/EV_v.1.1.py:384-391` (eski, 2026-08-09 hâli)
- `raw/CV_model_gurobi_exact.py:419-426` (yeni, 2026-08-22)
- `raw/EV_v.1.1.py:369-376` (yeni, 2026-08-22)

## Related

- [[karar_operasyonel_zaman_kaydirma_format_time]]
- [[cozum_raporlama_fonksiyonlari]]
