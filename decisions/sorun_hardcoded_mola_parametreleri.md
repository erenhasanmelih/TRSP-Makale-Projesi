---
title: Sorun — Sabit (Hardcoded) Mola Parametreleri
tags: [sorun, mola, kod-esnekliği, parametrizasyon]
source: raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx
date: 2026-08-09
status: güncel
---

# Sorun — Sabit (Hardcoded) Mola Parametreleri

## Sorun

Matematiksel model, mola zamanlarını esnek parametreler üzerinden dinamik olarak alıyor. Kod ise mola sürelerini ve zaman aralıklarını sabit değişkenler olarak doğrudan (hardcoded) kurguluyor:

```
break_duration = 3600   # Tam 1 saat
break_min = 13800       # 11:50 (+10/-10 dk tolerans alt sınırı)
break_max = 15000       # 12:10 (+10/-10 dk tolerans üst sınırı)
```

## Neden sorun

Farklı problem senaryoları (farklı vardiya saatleri, farklı mola politikaları) için modeli yeniden çalıştırmak, kaynak kodun değiştirilmesini gerektiriyor — parametrik hale getirilmediği sürece deneysel esneklik (ör. duyarlılık analizi, farklı senaryo karşılaştırmaları) kısıtlanıyor.

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- Kod: `raw/CV_model_gurobi_exact.py:70-72`, `raw/EV_v.1.1.py:156-158` (Stage 2 ingest'te doğrulandı)

## Related

- [[celiski_ogle_molasi_zorunlulugu]]
- [[karar_molasiz_erken_donus_kurali_kod]]
- [[sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar]]
