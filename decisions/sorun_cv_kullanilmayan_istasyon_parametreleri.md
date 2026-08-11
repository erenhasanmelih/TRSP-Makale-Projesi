---
title: Sorun (Kod, CV) — Kullanılmayan İstasyon-İlişkili Parametreler (Fc, alpha, g_c, k, lc0)
tags: [sorun, kod, cv, ölü-kod, istasyon]
source: raw/CV_model_gurobi_exact.py
date: 2026-08-09
status: güncel
---

# Sorun (Kod, CV) — Kullanılmayan İstasyon-İlişkili Parametreler

## Sorun

`CV_model_gurobi_exact.py:13-16`'daki `build_model()` fonksiyonuna geçirilen şu parametreler, fonksiyon gövdesinde (satır 18-197) **hiçbir kısıtta veya ifadede kullanılmıyor**:

- `Fc` — sadece kullanılmayan `alpha = m.addVars(Fc, Vc, ...)` değişkenini (satır 27) boyutlandırmak için var; `alpha` değişkeninin kendisi de hiçbir kısıtta geçmiyor.
- `g_c` — CV'deki EV'nin `g_e` (şarj süresi katsayısı) karşılığı olması muhtemel, ama hiç kullanılmıyor.
- `k` — amacı belirsiz, hiç kullanılmıyor.
- `lc0` — `__main__` bloğunda `data['lc0'] = 100000.0` olarak atanıyor (satır 381) ama `build_model` içinde hiç referans edilmiyor.
- `node_labels` — sadece `print_cv_solution`'da `data.get('node_labels', {})` üzerinden kullanılıyor, `build_model`'e geçirilen parametre olarak hiç kullanılmıyor.

## Neden önemli

`Fc` ve `alpha`'nın varlığı, geliştiricinin CV modeline bir istasyon/yakıt-maliyeti yapısı eklemeyi planladığını ama bunu hiçbir kısıtla tamamlamadığını gösteriyor — bu, [[sorun_sarj_yakit_istasyonlari_kodda_yok]]'ta tarif edilen eksikliğin **somut kod kanıtı**: iskelet var, kısıtlar yok.

## Uygulama (Faz 2, 2026-08-11) — bu sayfa doğrudan hedeflenmedi, ilgili bir düzeltme yapıldı

Bu sayfadaki `Fc`/`alpha`/`g_c`/`k`/`lc0` ölü kod tespiti **Faz 2'de değişmedi** — bu parametreler `src/CV_model_gurobi_fixed.py`'de de hâlâ kullanılmıyor (istasyon yapısı CV'ye eklenmedi, bkz. [[sorun_sarj_yakit_istasyonlari_kodda_yok]]). Ancak **ilgili ama ayrı bir CV tutarsızlığı** (A7) düzeltildi: `h_c` (mesafe başına tüketim oranı) önceden sabit `1.0`'dı, `EnergyConsumptionRate` XML'den hiç okunmuyordu — bu, istasyon eksikliğinden bağımsız ama aynı "CV'nin yakıt/enerji tarafı yarım kalmış" temasının bir başka örneğiydi. `src/xml_data_loader_fixed.py:249-269,289` ile düzeltildi, ayrıca araç-bazlı `h_c_v` sözlüğü eklendi. Detay: [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]].

## Sources

- `raw/CV_model_gurobi_exact.py:13-27`
- `src/xml_data_loader_fixed.py:249-269,289` (ilgili A7 düzeltmesi — Fc/alpha/g_c/k/lc0'ın kendisi hâlâ kullanılmıyor)

## Related

- [[sorun_sarj_yakit_istasyonlari_kodda_yok]]
- [[sources/2026-08-09-cv_model_gurobi_exact]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
