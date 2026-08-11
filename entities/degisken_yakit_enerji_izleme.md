---
title: Karar Değişkenleri — Yakıt/Enerji İzleme (yc/YC — CV, ye/YE — EV)
tags: [entity, karar-değişkeni, gurobi, yakıt, enerji, ev, cv]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Karar Değişkenleri — Yakıt/Enerji İzleme

CV ve EV modelleri paralel bir yakıt/enerji izleme yapısı kullanıyor:

| CV (`CV_model_gurobi_exact.py`) | EV (`EV_v.1.1.py`) | Anlamı |
|---|---|---|
| `yc[i]` (satır 25) | `ye[i]` (satır 99) | düğüme varıştaki yakıt/enerji seviyesi |
| `YC[i]` (satır 24) | `YE[i]` (satır 98) | düğümden ayrılıştaki yakıt/enerji seviyesi |
| `h_c` | `h_e` | mesafe başına tüketim katsayısı |
| — | `g_e` | şarj süresi katsayısı (EV'ye özgü, CV'de karşılığı yok) |
| `G[v]` | `Q[v]` | araç kapasitesi |

## CV tarafı (c20-c22, satır 146-171)

`yc[j] <= yc[i] - (h_c * d[i,j]) * x[i,j,v,t] + G[v] * (1 - x[i,j,v,t])` — doğrusal tüketim, dolum mekanizması yok. `YC[i] == yc[i]` (c22) — depoda dolum dışında hiçbir yerde şarj/dolum yok, çünkü istasyon kümesi kodda tanımlı değil (bkz. [[sorun_sarj_yakit_istasyonlari_kodda_yok]]).

## EV tarafı (c20-c22, satır 306-353)

Aynı tüketim mantığı, ama istasyon düğümlerinde (`i in S_set`) `YE[i] >= ye[i]` (c22_station_recharge_lb, satır 334) ile dolum serbest bırakılıyor; `c22_station_recharge_bigM` (350-353) dolum miktarını o düğümden çıkış yapan bir arc'ın (`outflow_s`) var olmasına bağlıyor. Şarj süresi, `c8_zaman_ilerleme` kısıtındaki `charge_time_i = g_e * (YE[i]-ye[i])` terimiyle zaman eksenine yansıtılıyor (satır 165, 271) — bkz. [[partial_recharging]].

## Güncelleme (Faz 2, 2026-08-11)

`src/`'deki kopyalarda `yc/YC` (CV) ve `ye/YE` (EV) artık **çok-indisli**: `(Np, K)` — yani her düğüm `i` için ayrı bir değer değil, her (düğüm, `k`=araç-ekip çifti) için ayrı bir değer tutuluyor (`yc[i,kk]`, `YE[i,k]` vb.), çünkü `x` de aynı `k` indeksine göre 3B'ye indirgendi (bkz. [[degisken_x_arc_tahsisi]]). Kapasite artık `Q_of_k[k]`/`G_of_k[k]` ile araç-bazlı doğru şekilde uygulanıyor (`YE[i,k].UB = Q_of_k[k]`, `src/EV_v_1_1_fixed.py:198-199`) — heterojen filo (farklı kapasiteli araçlar) artık doğru destekleniyor.

Tüketim katsayısı da artık araç-bazlı: `he_of_k[k]` (EV), `hc_of_k[k]` (CV) — `h_e_v`/`h_c_v` sözlüklerinden (A7 düzeltmesiyle XML'den okunuyor, bkz. [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]) geliyor.

**A1 düzeltmesi (EV, kritik):** `c20`'nin istasyon çıkış yaylarında da yazılıp `c21`'i (gerçek şarj sonrası enerji) her zaman ezdiği, dolayısıyla şarjın hiç akışa yansımadığı sorunu giderildi (`if i in S_set: continue`, `src/EV_v_1_1_fixed.py:482-483`). Detay: [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]. **Kalan sorun:** `ye`/`YE` arası hâlâ sadece `<=` eşitsizlik, eşitlik yok — raporlama güvenilirliği etkileniyor, bkz. [[sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi]].

Tam refaktör kaydı: [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]].

## Sources

- `raw/CV_model_gurobi_exact.py:24-25,146-171`
- `raw/EV_v.1.1.py:98-99,306-353`
- `src/CV_model_gurobi_fixed.py:32-49,116-117,377-422`
- `src/EV_v_1_1_fixed.py:118-130,198-199,472-548`

## Related

- [[sorun_sarj_yakit_istasyonlari_kodda_yok]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
- [[partial_recharging]]
- [[klon_dugum_node_replication]]
- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
- [[sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi]]
