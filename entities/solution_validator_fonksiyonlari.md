---
title: Doğrulayıcı Fonksiyonlar — validate_solution, summarize_trips
tags: [entity, fonksiyon, dogrulama, v1.1]
source: raw/solution_validator.py
date: 2026-08-22
status: güncel
---

# Doğrulayıcı Fonksiyonlar — validate_solution, summarize_trips

`raw/solution_validator.py`'de tanımlı, Gurobi çözümü sonrası çalıştırılan iki ana fonksiyon (tam kaynak analizi: [[sources/2026-08-22-solution_validator]]).

## `validate_solution(model, data, x_key_is_triple=True) -> (ok, findings)`

`model._x`/`model._tau`/`model._K` üzerinden iki koşulu denetler:

1. **Sefer sırası:** aynı kaynağın (`kk`) art arda seferleri kronolojik mi (2. sefer, 1. sefer bitmeden başlamıyor mu)?
2. **Araç çakışması:** aynı fiziksel aracı (`kk[0]`) paylaşan farklı ekipler (`kk1 != kk2` ama aynı araç) çakışan saatlerde mi kullanılmış?

`ok=False` ise `findings` listesinde "SEFER SIRASI İHLALİ: ..." veya "ARAÇ ÇAKIŞMASI: ..." biçiminde insan-okunur Türkçe açıklamalar döner.

## `summarize_trips(model, data) -> dict`

Teşhis amaçlı: hangi kaynağın (`kk`) kaç seferi olduğunu (`len(trips) > 1` olanları) özetler.

## Yardımcı fonksiyonlar

- `_reconstruct_trips(arcs)` — `print_cv_solution`/`print_ev_solution` ile aynı arc→trip ayrıştırma mantığının bağımsız bir kopyası (üç dosyada da aynı algoritma tekrarlanıyor — bkz. [[cozum_raporlama_fonksiyonlari]]).
- `_trip_time_window(trip, tau, kk, st, tt)` — bir seferin [çıkış, dönüş] aralığını hesaplar.

## Neden önemli

Bu fonksiyonlar, [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]'nda belgelenen CV-27/28 ve EV-22/23 kısıtlarının **doğrudan kanıt kaynağıdır** — RC7 problem setinde `CV_3` aracının iki ekip tarafından çakışan saatlerde kullanıldığı, bu doğrulayıcıyla tespit edilmiştir (bkz. "Değişiklik Raporu - v1.1.docx", madde 3).

## Sources

- `raw/solution_validator.py:24-156`

## Related

- [[karar_rc13_asgari_paket_uygulamasi]] (Ö2 aggregate modda Kontrol 2 (araç çakışması) sweep-line tabanlı |V| kapasitesi kontrolüne yeniden yazıldı)
- [[sources/2026-08-22-solution_validator]]
- [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]
- [[degisken_z_arac_ekip_atama]]
- [[cozum_raporlama_fonksiyonlari]]
- [[build_model_fonksiyonu]]
