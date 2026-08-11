---
title: Karar (Kod) — Molasız Görevler İçin Erken Dönüş Kuralı
tags: [karar, kod-esnekliği, mola, big-m]
source: raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx
date: 2026-08-09
status: güncel
---

# Karar (Kod) — Molasız Görevler İçin Erken Dönüş Kuralı

## Karar

Kod, `mola_yoksa_erken_donus_{i}_{v}_{t}` isimli fazladan bir kısıt barındırıyor: eğer teknisyen gün içinde mola hakkını kullanmadıysa, depoya dönüş saatinin daha erken (maksimum mola başlangıç süresi sınırlarında) olması Big-M yöntemiyle zorunlu kılınıyor.

## Gerekçe

Bu kısıt, [[celiski_ogle_molasi_zorunlulugu]]'nda tanımlanan model-kod çelişkisinin (mola model'de zorunlu, kodda opsiyonel) bir telafi mekanizması gibi görünüyor: mola atlanırsa en azından iş günü daha kısa tutuluyor, tamamen kuralsız bırakılmıyor. Modelde mola zaten zorunlu olduğu için böyle bir alternatif dönüş kısıtı tanımlanmamış.

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- Kod: `raw/CV_model_gurobi_exact.py:98-107`, `raw/EV_v.1.1.py:177-194` (Stage 2 ingest'te doğrulandı)

## Related

- [[celiski_ogle_molasi_zorunlulugu]]
- [[sorun_hardcoded_mola_parametreleri]]
