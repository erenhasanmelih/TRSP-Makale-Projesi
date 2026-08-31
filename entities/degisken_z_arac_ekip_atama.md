---
title: Karar Değişkeni — z / z_veh (Araç-Ekip Atama)
tags: [entity, karar-degiskeni, gurobi, tekillik, v1.1]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-22
status: güncel
---

# Karar Değişkeni — z (CV) / z_veh (EV)

`z[v,t] ∈ {0,1}` (CV, `CV_model_gurobi_exact.py:108`) / `z_veh[v,t] ∈ {0,1}` (EV, `EV_v.1.1.py:124`) — "araç `v`, bugün ekip `t`'ye atandı mı?" sorusunun cevabı. Gurobi'nin optimizasyon sırasında serbestçe karar verdiği bir değişken; kodda hiçbir yerde sabit bir atama yok.

## Bağlı olduğu kısıtlar

- **CV-4/EV-4 (çoklu sefer):** `sum(x[0,j,kk]) <= 3*z[kk]` — `z[kk]=0` ise kaynak hiç depodan çıkamaz.
- **CV-27/EV-22 (araç-ekip tekilliği):** `sum(z[v,t] for t in T) <= 1` — her araç günde en fazla bir ekibe atanabilir.
- **CV-28/EV-23 (teknisyen tekilliği):** `sum(z[v,t] for v,t if tech in crew_members[t]) <= 1` — her ham teknisyen günde en fazla bir aktif atamada yer alabilir.

Tam kısıt metinleri ve gerekçe: [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]].

## v1.0 → v1.1 bağlamı

Önceki `raw/` sürümünde bu değişken yoktu (tek-sefer modelinde araç-ekip ataması örtük olarak `x[0,j,v,t]`'nin kendisiyle sınırlıydı, ayrı bir tekillik kısıtına gerek yoktu). `z`/`z_veh`, çoklu seferin (CV-4/EV-4, ≤3) getirdiği yeni bir riski (aynı aracın farklı ekiplerle çakışan biçimde kullanılması) kapatmak için eklendi — bkz. [[solution_validator_fonksiyonlari]] (bu riski tespit eden doğrulayıcı).

## Sources

- `raw/CV_model_gurobi_exact.py:100-184`
- `raw/EV_v.1.1.py:120-195`

## Related

- [[karar_rc13_asgari_paket_uygulamasi]] (Ö2: homojen filoda z artık `(v,t)` değil yalnızca `t` ile indeksleniyor — `Σ_t z[t] <= |V|`)
- [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]
- [[solution_validator_fonksiyonlari]]
- [[degisken_x_arc_tahsisi]]
- [[kk_name_degisken_temiz_isimlendirme]]
- [[celiski_single_trip_vs_multitrip]]
