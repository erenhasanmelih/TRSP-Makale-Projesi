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

## Güncelleme (2026-08-22) — imzalar korunmuş, gövde tamamen yeniden yazılmış

`raw/CV_model_gurobi_exact.py` ve `raw/EV_v.1.1.py`'nin 2026-08-22 yeniden yazımında **her iki `build_model()`'in üst düzey imza tarzı korunmuş** (CV hâlâ pozisyonel parametre listesi + `a_max=None, node_labels=None, crew_members=None` opsiyonelleri eklendi; EV hâlâ tek `data` dict). Ama gövdeler baştan yazılmış:

| | CV (`CV_model_gurobi_exact.py:23-416`, 2026-08-22) | EV (`EV_v.1.1.py:28-366`, 2026-08-22) |
|---|---|---|
| Arc tahsisi | `x[i,j,kk]`, 3B | `x[i,j,kk]`, 3B |
| Yakıt/enerji | `YC`/`yc` (düğüm-bazlı, değişmedi) | `YE`/`ye` (düğüm-bazlı, değişmedi) |
| İstasyon desteği | `real_stations` filtreli, hâlâ boş (`Fc=[0]`) | `S`/`S_set`, aktif (`Kalabak_Info4ChargingStations.xml`) |
| Ekip çakışma önleme | Yok (yerine `z`+CV-28) | **Kaldırıldı** (yerine `z_veh`+EV-23) |
| Çoklu sefer | **Var (CV-4, ≤3)** | **Var (EV-4, ≤3, ilk kez)** |
| Tekillik | `z`, CV-27/28 (yeni) | `z_veh`, EV-22/23 (yeni) |
| `y_route[t]` | Yok | **Kaldırıldı** |
| İsimlendirme | `kk_name` (yeni) | `kk_name` (yeni) |

İki fonksiyonun imza tarzı farkı (pozisyonel liste vs dict) hâlâ duruyor — aşağıdaki "Not" bölümündeki gözlem geçerliliğini koruyor. Detay: [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]], [[sources/2026-08-22-ev_v1_1_rewrite]], [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]].

## Sources

- `raw/CV_model_gurobi_exact.py:13-197` (eski, 2026-08-09 hâli)
- `raw/EV_v.1.1.py:65-381` (eski, 2026-08-09 hâli)
- `raw/CV_model_gurobi_exact.py:23-416` (yeni, 2026-08-22)
- `raw/EV_v.1.1.py:28-366` (yeni, 2026-08-22)

## Related

- [[degisken_x_arc_tahsisi]]
- [[degisken_yakit_enerji_izleme]]
- [[gurobi_mip_cozucusu]]
