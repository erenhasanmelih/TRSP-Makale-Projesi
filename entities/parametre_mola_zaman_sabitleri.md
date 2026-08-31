---
title: Parametre — Mola Zaman Sabitleri (break_duration, break_min, break_max)
tags: [entity, parametre, mola, hardcoded]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Parametre — Mola Zaman Sabitleri

Her iki dosyada birebir aynı üç sabit (CV: satır 70-72, EV: satır 156-158):

```python
break_duration = 3600   # Tam 1 Saat
break_min = 13800       # 11:50 (+10/-10 dk tolerans alt sınırı)
break_max = 15000       # 12:10 (+10/-10 dk tolerans üst sınırı)
```

`format_time()`'daki `+28800` kaymasıyla birlikte yorumlandığında: model saniyesi `13800` → gerçek saat `13800+28800=42600s = 11:50`; `15000` → `43800s = 12:10`. Bu nedenle yorum satırındaki saatler doğru.

Bu sabitler [[sorun_hardcoded_mola_parametreleri]]'nde tanımlanan sorunun doğrudan kod kanıtıdır — model tarafında parametrik olması beklenirken kodda sabit.

## Güncelleme (2026-08-22) — sabitler build_model'den kalktı, mola penceresi genişledi

`raw/CV_model_gurobi_exact.py` ve `raw/EV_v.1.1.py`'nin 2026-08-22 yeniden yazımında `break_duration`/`break_min`/`break_max` adlı ayrı sabitler **artık `build_model()` içinde tanımlı değil**. Mola penceresi artık doğrudan `el[t]`/`ll[t]` (ekip mola aralığı) parametreleri üzerinden geliyor; bu parametrelerin varsayılan değerleri `raw/xml_data_loader.py`'nin `prepare_cv_data_from_instance`/`prepare_ev_data_from_instance` imzalarına taşındı: `el_val=14400.0` (12:00), `ll_val=21600.0` (14:00) — yani **~2 saatlik bir pencere**, eski `break_min=13800`(11:50)/`break_max=15000`(12:10) ~20 dakikalık pencereden belirgin biçimde geniş (doğrulanmamış, statik okumaya dayalı bir gözlem — davranış değişikliği olabilir).

Mola *süresinin* kendisi (`3600` saniye = 1 saat) artık yalnızca raporlama fonksiyonlarında (`print_cv_solution`/`print_ev_solution`) literal olarak kullanılıyor, `build_model()` kısıtlarında ayrı bir "süre" parametresi yok — mola süresi kısıt tarafında `(ll[t_]-el[t_])` farkına gömülü.

Bu, sayfanın ana iddiasını (mola parametrelerinin sabit/hardcoded olması) **değiştirmiyor** — sabitler hâlâ var, sadece konumu (`build_model` → `xml_data_loader` fonksiyon imzası varsayılanları) ve isimleri değişti. Detay: [[sources/2026-08-22-xml_data_loader_v1_1]].

## Sources

- `raw/CV_model_gurobi_exact.py:70-72` (eski, 2026-08-09 hâli)
- `raw/EV_v.1.1.py:156-158` (eski, 2026-08-09 hâli)
- `raw/xml_data_loader.py:218-221,278-281` (yeni, 2026-08-22 — `es_val/ls_val/el_val/ll_val` varsayılanları)

## Related

- [[sorun_hardcoded_mola_parametreleri]]
- [[karar_operasyonel_zaman_kaydirma_format_time]]
- [[celiski_ogle_molasi_zorunlulugu]]
- [[sorun_rapor_mola_suresi_3600_vs_ll_el]]
