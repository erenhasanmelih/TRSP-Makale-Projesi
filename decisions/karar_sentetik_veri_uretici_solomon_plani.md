---
title: Karar (Planlı) — Solomon-Tipi Sentetik Veri Üretici Modül
tags: [karar, planlı, veri-üretimi, stress-test, solomon]
source: raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx
date: 2026-08-09
status: güncel
---

# Karar (Planlı) — Solomon-Tipi Sentetik Veri Üretici Modül

## Karar

Müşteri lokasyonlarını Solomon standartlarına göre (Rastgele-R, Kümelenmiş-C, Yarı Kümelenmiş-RC) türeten bir Python betiği yazılacak. 5 farklı görev tipi (P1: 5G Montaj, P2: Fiber vb.) ve 60-120 dakika hizmet süreleri sentetik müşterilere rastgele atanacak; SLA kurallarına uygun gerçekçi zaman pencereleri türetilecek.

## Gerekçe

Algoritmaların sınırlarını (stress-test) test etmek ve farklı coğrafi/operasyonel senaryoların etkilerini şeffafça göstermek; gerçek verilerin eksik/gizlilik kısıtlı olduğu durumlarda modelin her türlü yoğunluk/dağılım senaryosunda stabil çalıştığını akademik olarak ispatlamak. Ayrıca R/C/RC veri setleri üzerinden EV'nin kümelenmiş (C) verilerde başarılı, dağınık (R) verilerde menzil kaygılı olduğuna dair teorik argüman somutlaştırılacak.

## İlişki

Mevcut `raw/problem_sets/` ve `raw/trsp_problem_sets/` klasörlerindeki R/C/RC XML dosyaları muhtemelen bu üretici modülün (veya benzer bir Solomon-tabanlı sürecin) çıktısı — Stage 2 dışı, veri kaynağı olarak ileride ayrıca ingest edilebilir.

## Sources

- `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx`

## Related

- [[karar_3_asamali_rolling_horizon_sistem_mimarisi]]
