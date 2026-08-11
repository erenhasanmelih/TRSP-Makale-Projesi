---
title: build_model() Fonksiyonu (CV ve EV)
tags: [entity, fonksiyon, gurobi, model-kurulumu]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# build_model() Fonksiyonu (CV ve EV)

Her iki dosyada da `build_model` adında, Gurobi modelini (karar değişkenleri + kısıtlar + amaç fonksiyonu) kurup döndüren bir fonksiyon var — ama imzaları farklı:

| | CV (`CV_model_gurobi_exact.py:13-197`) | EV (`EV_v.1.1.py:65-381`) |
|---|---|---|
| İmza | `build_model(N, N0, C, Vc, V, T, Ti, Fc, A, d, tt, st, G, ec, lc, es, ls, el, ll, h_c, g_c, k, lc0, node_labels=None)` — 24 pozisyonel/opsiyonel parametre | `build_model(data)` — tek dict |
| Yakıt/enerji değişkeni | `YC`/`yc` | `YE`/`ye` |
| İstasyon desteği | Yok (parametreler tanımlı ama kullanılmıyor: `Fc`, `alpha`) | Var (`S`/`S_set`, `c22_station_recharge_*`) |
| Ekip çakışma önleme | Yok | Var (`route_start`/`route_end`/`ord_*`, satır 225-299) |
| `y_route[t]` | Yok | Var |

## Not

İki fonksiyonun imza tarzının bu kadar farklı olması (pozisyonel parametre listesi vs dict), muhtemelen EV modelinin CV'den sonra, veri hazırlama katmanı (`prepare_ev_data_from_instance`) daha esnek hale getirilerek yazıldığını gösteriyor. Bu, makale/kod tutarlılığı açısından refactoring ihtiyacı olabilir ama bu ingest kapsamında sadece gözlem olarak not düşülüyor.

## Sources

- `raw/CV_model_gurobi_exact.py:13-197`
- `raw/EV_v.1.1.py:65-381`

## Related

- [[sources/2026-08-09-cv_model_gurobi_exact]]
- [[sources/2026-08-09-ev_v1_1]]
- [[degisken_x_arc_tahsisi]]
- [[degisken_yakit_enerji_izleme]]
- [[gurobi_mip_cozucusu]]
