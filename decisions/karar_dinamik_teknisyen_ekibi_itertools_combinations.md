---
title: Karar (Kod) — Dinamik Teknisyen Ekibi Oluşturma (itertools.combinations)
tags: [karar, kod-esnekliği, ekip-oluşturma, teknisyen]
source: raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx
date: 2026-08-09
status: güncel
---

# Karar (Kod) — Dinamik Teknisyen Ekibi Oluşturma (itertools.combinations)

## Karar

Geliştirici, matematiksel modelde sadece bireysel teknisyenleri temsil eden T kümesine ek olarak, kodda `itertools.combinations(active_techs, 2)` fonksiyonunu kullanarak teknisyenleri ikili ekipler halinde eşleştirmiş ve yeteneklerini birleştirerek yeni bir "ekip (crew)" listesi oluşturmuş.

## Gerekçe (çıkarım)

Bu, modelde tanımlanmamış ama operasyonel gerçekliği yansıtan bir esneklik — iki teknisyenin birlikte çalışarak birleşik yetkinliğe sahip bir ekip oluşturması, tek başına yetkin olmayan görevlere erişimi genişletiyor.

## İlişki

Full Path.docx'teki planlanan [[index_reduction_3b]] ("araç ve ekip önceden eşleştirilecek") varsayımıyla bu dinamik ekip oluşturma yaklaşımının nasıl uzlaşacağı açık bir soru — index reduction planı statik eşleştirme varsayarken, kod dinamik/kombinasyonel eşleştirme yapıyor.

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- Kod: `raw/CV_model_gurobi_exact.py:414-417`, `raw/EV_v.1.1.py:696-700` (Stage 2 ingest'te doğrulandı)

## Related

- [[index_reduction_3b]]
- [[uyumluluk_matrisi]]
- [[sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar]]
