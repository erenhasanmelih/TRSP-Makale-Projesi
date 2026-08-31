---
title: Karar (Kod) — Operasyonel Zaman Kaydırma (format_time / +28800)
tags: [karar, kod-esnekliği, raporlama, zaman-formatı]
source: raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx
date: 2026-08-09
status: güncel
---

# Karar (Kod) — Operasyonel Zaman Kaydırma (format_time / +28800)

## Karar

Kod yapısında, optimizasyon sonrası rotaların yazdırıldığı `print_cv_solution` fonksiyonunda saniyeleri saat formatına dönüştüren bir zaman kaydırması var: `shifted_seconds = seconds + 28800`. Bu sayede modelin 0. saniyesi, operasyonel referans noktası olan sabah 08:00'e karşılık geliyor.

## Gerekçe

Teorik modelin ilgilenmediği bir arayüz/çıktı formatlama adımı — model saniye cinsinden 0'dan başlayan bir zaman ekseni kullanırken, insan tarafından okunabilir operasyonel raporlar için bu 08:00 referans kaydırması uygulanıyor. Model-kod çelişkisi değil, saf bir sunum/raporlama kararı.

## Güncelleme (2026-08-22)

Mantık ve `+28800` kayması `raw/`'un 2026-08-22 yeniden yazımında birebir korunmuş, sadece satır numaraları değişti (CV `419-426`, EV `369-376`) — bkz. [[format_time_fonksiyonu]] güncellemesi.

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- Kod: `raw/CV_model_gurobi_exact.py:200-207`, `raw/EV_v.1.1.py:384-391` (eski, 2026-08-09 hâli, Stage 2 ingest'te doğrulandı)
- `raw/CV_model_gurobi_exact.py:419-426`, `raw/EV_v.1.1.py:369-376` (yeni, 2026-08-22)

## Related

- [[sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar]]
