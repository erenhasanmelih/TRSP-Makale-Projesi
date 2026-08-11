---
title: Birleşik k İndeksi ve Yardımcı Haritalar (K_pairs, KK, XK, arc_ks, out_nodes, in_nodes, ...)
tags: [entity, faz2, mip-boyut-küçültme, indeksleme]
source: src/EV_v_1_1_fixed.py; src/CV_model_gurobi_fixed.py
date: 2026-08-11
status: güncel
---

# Birleşik k İndeksi ve Yardımcı Haritalar

Faz 2'nin [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]] refaktörüyle `src/EV_v_1_1_fixed.py:113-206` ve `src/CV_model_gurobi_fixed.py:32-116`'da kurulan, `x[i,j,v,t]` (4B) → `x[i,j,k]` (3B) indirgemesini destekleyen veri yapıları. `raw/`'da bu yapıların hiçbiri yok.

| Yapı | Tanım | Amaç |
|---|---|---|
| `K_pairs` | `[(v, t) for v in V for t in T]` — tüm (araç, ekip) çiftlerinin listesi | Birleşik `k` indeksinin kaynağı |
| `KK` | `range(len(K_pairs))` | `k`'nin alabileceği tamsayı değer kümesi |
| `k_veh[k]` / `k_crew[k]` | `K_pairs[k]`'nin bileşenlerine erişim | Bir `k`'den araç/ekibi geri çözmek |
| `K_of_crew[t]` | Ekip `t`'yi içeren tüm `k` değerlerinin listesi | Ekip-bazlı toplama (örn. mola kısıtları) |
| `K_of_veh[v]` | Araç `v`'yi içeren tüm `k` değerlerinin listesi | Araç-bazlı toplama (örn. kapasite kısıtları) |
| `Q_of_k[k]` (EV) / `G_of_k[kk]` (CV) | `k`'nin aracının kapasitesi | Heterojen filo (A2) — kapasite artık araç-bazlı doğru uygulanıyor |
| `he_of_k[k]` (EV) / `hc_of_k[kk]` (CV) | `k`'nin aracının tüketim oranı | A7 düzeltmesiyle XML'den okunan `h_e_v`/`h_c_v`'ye dayanıyor |
| `_crew_allowed(node, t)` | Ekip `t`'nin düğüm `node`'a yetkinlik açısından uygun olup olmadığını döndüren fonksiyon | A5 — uyumsuz kombinasyonları filtrelemek |
| `XK` | `(i, j, k)` üçlülerinin listesi — sadece `_crew_allowed` filtresinden geçen, yani geçerli arc-k kombinasyonları | `x = m.addVars(XK, ...)`'in doğrudan girdisi |
| `XK_set` | `XK`'nin `set()` hâli | O(1) üyelik testi (`(i,j,k) in XK_set`) |
| `arc_ks[(i,j)]` | `(i,j)` arc'ı için geçerli tüm `k` değerleri | Belirli bir arc üzerindeki tüm k'leri toplamak |
| `out_nodes[(i,k)]` | `k` için `i`'den çıkış yapılabilen düğümler | Akış denge kısıtlarında çıkış toplamı |
| `in_nodes[(j,k)]` | `k` için `j`'ye giriş yapılabilen düğümler | Akış denge kısıtlarında giriş toplamı |

## Neden önemli

Bu haritalar olmadan `x[i,j,k]`'nin 3B hâli, eski 4B döngü yapılarıyla (her kısıtta `for v in V: for t in T:` iç içe döngüsü) verimsiz biçimde yeniden inşa edilirdi. `XK`/`arc_ks`/`out_nodes`/`in_nodes` sayesinde hem `_crew_allowed` filtresi tek bir yerde uygulanıp tüm modele yayılıyor (A5) hem de akış denge kısıtları (`c2-c6`) doğrudan bu ön-hesaplanmış listeler üzerinden kuruluyor.

## Sources

- `src/EV_v_1_1_fixed.py:113-206`
- `src/CV_model_gurobi_fixed.py:32-116`

## Related

- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
- [[degisken_x_arc_tahsisi]]
- [[degisken_yakit_enerji_izleme]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
- [[uyumluluk_matrisi]]
- [[colored_tsp]]
