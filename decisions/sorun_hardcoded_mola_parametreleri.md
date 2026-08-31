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

## Güncelleme (2026-08-22)

Sabitlerin konumu değişti (artık `raw/xml_data_loader.py`'nin fonksiyon imzası varsayılanlarında, `build_model()` içinde değil) ve mola penceresi genişlemiş görünüyor (~20 dk → ~2 saat, doğrulanmadı). Sorunun özü (mola zamanlarının kod içinde sabit olması, model tarafında parametrik olmaması) **değişmedi**. Tam detay: [[parametre_mola_zaman_sabitleri]] güncellemesi, [[sources/2026-08-22-xml_data_loader_v1_1]].

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- Kod: `raw/CV_model_gurobi_exact.py:70-72`, `raw/EV_v.1.1.py:156-158` (eski, 2026-08-09 hâli, Stage 2 ingest'te doğrulandı)
- `raw/xml_data_loader.py:218-221,278-281` (yeni, 2026-08-22 — sabitlerin taşındığı yer)

## Related

- [[celiski_ogle_molasi_zorunlulugu]]
- [[karar_molasiz_erken_donus_kurali_kod]]
- [[sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar]]
