---
title: solution_validator.py — Çözüm Sonrası Tutarlılık Doğrulayıcısı (Yeni Dosya)
tags: [kaynak, kod, dogrulama, cv, ev, v1.1]
source: raw/solution_validator.py
date: 2026-08-22
status: güncel
---

# solution_validator.py — Çözüm Sonrası Tutarlılık Doğrulayıcısı

## Amaç

`raw/`'a 2026-08-22'de eklenen tamamen yeni bir dosya (156 satır). CV/EV modellerinin ürettiği çözümleri, kısıtların **garanti etmediği** ama operasyonel olarak zorunlu iki noktada denetliyor:

1. Çoklu sefer (CV-4/EV-4) kullanan bir kaynağın (k) art arda seferleri kronolojik sıralı mı?
2. Aynı fiziksel aracı paylaşan farklı ekipler aynı gün çakışan saatlerde mi kullanılmış?

Dosyanın kendi docstring'i bu iki koşulun mevcut kısıtlarda (CV-1..26, EV-1..21) **doğrudan yer almadığını**, bu yüzden teorik olarak ihlal edilebileceğini açıkça belirtiyor (satır 15-19) — bkz. [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]'ndaki "Bilinen sınır" notu.

## Fonksiyon envanteri

- **`_reconstruct_trips(arcs)`** (satır 24-50): bir kaynağın yaylarını, `print_cv_solution`/`print_ev_solution` ile birebir aynı mantıkla ayrı seferlere (trip) ayırıyor.
- **`_trip_time_window(trip, tau, kk, st, tt)`** (satır 53-66): bir seferin [çıkış, dönüş] zaman aralığını hesaplıyor; çıkış zamanı ilk müşterinin varışından geriye doğru türetiliyor (CV-26/EV-21'in geri alınmasının rapor katmanındaki telafisiyle aynı desen).
- **`validate_solution(model, data, x_key_is_triple=True)`** (satır 69-141): ana doğrulama fonksiyonu. `model._x`, `model._tau`, `model._K` üzerinden çalışıyor (bu, `build_model()`'in modele bağladığı öznitelikler — bkz. [[build_model_fonksiyonu]]). İki kontrolü de yapıyor: (1) aynı `kk`'nin seferleri kronolojik mi, (2) aynı aracı (`kk[0]`) paylaşan farklı `kk`'ler çakışıyor mu. `(ok: bool, findings: list[str])` döndürüyor; `findings` insan-okunur Türkçe ihlal açıklamaları.
- **`summarize_trips(model, data)`** (satır 144-156): teşhis amaçlı, kaç kaynağın kaç seferi olduğunu özetliyor.

## Bağlam — bu dosya nereden geldi

"Değişiklik Raporu - v1.1.docx" (madde 3), bu doğrulayıcının CV'nin RC7 sonucunda **gerçek bir hata** (aynı fiziksel aracın `CV_3` iki farklı ekip tarafından çakışan saatlerde kullanılması) bulduğunu, bunun da `z`/CV-27/CV-28 kısıtlarının eklenmesine yol açtığını belirtiyor. Yani bu dosya, [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]'nın **kanıt kaynağıdır**.

## Not — henüz hiçbir yerde çağrılmıyor

Ne `CV_model_gurobi_exact.py` ne `EV_v.1.1.py`'nin `__main__` bloğu bu modülü import edip çağırıyor (grep ile doğrulandı — sadece kendisi ve iki docx referans içeriyor). Yani doğrulama, üretim akışının bir parçası değil, ayrı bir test/geliştirme aracı gibi kullanılmış olmalı (Değişiklik Raporu'ndaki "Birleşik Final Testi" bölümünde elle çağrıldığı anlaşılıyor).

## Sources

- `raw/solution_validator.py` (tam dosya, 156 satır, 2026-08-22)
- `yeni dosyalarım/Matematiksel_Model_rev_v1.1/Değişiklik Raporu - v1.1.docx` (madde 3, 5.3)
- `yeni dosyalarım/Codes_rev_v1.1/solution_validator.py`

## Related

- [[solution_validator_fonksiyonlari]]
- [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]
- [[degisken_z_arac_ekip_atama]]
- [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]]
- [[sources/2026-08-22-ev_v1_1_rewrite]]
