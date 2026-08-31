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

## Güncelleme (2026-08-22) — artık yalnızca CV'de var

`raw/`'un 2026-08-22 yeniden yazımında bu kısıt CV tarafında korunmuş (`CV14_erken_donus`, `CV_model_gurobi_exact.py:289-302`) ama **EV tarafında artık yok** — yeni `EV_v.1.1.py`'de analog bir kısıt bulunamadı. Bu tutarlı bir değişiklik: EV'nin molası hem eski hem yeni kodda zorunlu (`==`, EV-12) olduğu için "mola kullanılmadıysa erken dön" telafisine hiç ihtiyaç yok — yalnızca CV'nin molası opsiyonel olduğu için bu kısıt CV'ye özgü kaldı. Detay: [[celiski_ogle_molasi_zorunlulugu]] (ÇÖZÜLDÜ bölümü).

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- Kod: `raw/CV_model_gurobi_exact.py:98-107`, `raw/EV_v.1.1.py:177-194` (eski, 2026-08-09 hâli, Stage 2 ingest'te doğrulandı)
- `raw/CV_model_gurobi_exact.py:289-302` (yeni, 2026-08-22 — yalnızca CV'de)

## Related

- [[sorun_rc20_darbogaz_kok_neden_analizi]] (**bu kısıtın beklenmedik bir sonucu**: CV-14, molasını kullanmayan bir CV kaynağını `ll`=21 600 s'ye kadar depoya dönmeye zorladığı için CV'nin "opsiyonel mola" esnekliği **kapasite avantajına dönüşmez** — molalı 25 200 s vs. molasız 21 600 s. Bu yüzden CV, EV ile aynı `Σst ≤ 25 200` duvarına çarpar ve RC20 CV de infeasible olur)
- [[celiski_ogle_molasi_zorunlulugu]]
- [[sorun_hardcoded_mola_parametreleri]]
