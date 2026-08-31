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

## Güncelleme (2026-08-22)

Mantık `raw/`'un 2026-08-22 yeniden yazımında da birebir korunmuş, sadece satır numaraları değişti: CV `705-709`, EV `632-636`. Ayrıca artık `crew_members` sözlüğü de aynı döngüde kuruluyor ve `data['crew_members']`'e yazılıyor — bu, yeni CV-28/EV-23 teknisyen tekillik kısıtının girdisi (bkz. [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]).

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- Kod: `raw/CV_model_gurobi_exact.py:414-417`, `raw/EV_v.1.1.py:696-700` (eski, 2026-08-09 hâli, Stage 2 ingest'te doğrulandı)
- `raw/CV_model_gurobi_exact.py:705-709`, `raw/EV_v.1.1.py:632-636` (yeni, 2026-08-22)

## Güncelleme (2026-08-31) — `[0]` seçimi düzeltildi

`tech = skill_tech_map[skill][0]` satırı (`raw/EV_v.1.1.py:1188`,
`raw/CV_model_gurobi_exact.py:1087`) **düzeltildi**: artık her beceriden
yalnızca ilk teknisyen değil, `skill_tech_map[skill]` listesindeki TÜM
teknisyenler aktifleştiriliyor. Bkz. [[karar_5_8_teknisyen_bug_fix]].
`itertools.combinations(active_techs, 2)` mantığının kendisi (bu sayfanın
konusu) değişmedi — yalnızca girdi kümesi (`active_techs`) artık eksiksiz.

## Related

- [[karar_5_8_teknisyen_bug_fix]] (bu sayfadaki `[0]` seçiminin düzeltilmiş hâli, UYGULANDI)
- [[sorun_rc20_darbogaz_kok_neden_analizi]] (**bu kurulumun kritik yan etkisi**: `tech = skill_tech_map[skill][0]` satırı — `raw/EV_v.1.1.py:1188`, `raw/CV_model_gurobi_exact.py:1087` — `raw/Info4Employee.xml`'deki 8 teknisyenin yalnızca 5'ini aktifleştirir; TECH_002/004/006 hiç kullanılmaz. EV-23/CV-28 ile birlikte bu, n ≥ 20 örneklerinde modeli **infeasible** yapar; bu bulgu 2026-08-31'de düzeltildi, bkz. [[karar_5_8_teknisyen_bug_fix]])
- [[index_reduction_3b]]
- [[uyumluluk_matrisi]]
- [[sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar]]
