---
title: Karar (Faz 2, C2) — Tight Big-M Uygulaması
tags: [karar, faz2, big-m, c2, mip-performans]
source: src/EV_v_1_1_fixed.py; src/CV_model_gurobi_fixed.py
date: 2026-08-11
status: güncel
---

# Karar (Faz 2, C2) — Tight Big-M Uygulaması

## Karar

4 kısıt grubunda sabit `100000.0` yerine türetilmiş (duruma özgü) M değerleri kondu:

| Kısıt grubu | Eski M | Yeni M (formül) |
|---|---|---|
| `c8` zaman ilerlemesi | `100000.0` | `M8 = tau_ub[i] + st[i] + break_duration (+ istasyonsa şarj süresi üst sınırı)` |
| Mola başlama alt/üst sınırı | `100000.0` | `M_mola_ust = max(0, tau_ub[i] + st[i] - break_max)` |
| Molasız erken dönüş | `100000.0` | `M_erken = max(0, tau_ub[i] + st[i] + tt[i,0] - break_max)` |
| `c_full_depot_lb/ub` | `100000.0` | `big_m_full = max(0, Q_of_k[k] - depart_use)` (EV) / `max(0, G_of_k[kk] - depart_use)` (CV) |
| `c20/c21` | `100000.0` | `Q_of_k[k]`/`G_of_k[k]` tabanlı (bkz. [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]) |

Konum: `src/EV_v_1_1_fixed.py` (çoklu satır: 272-283, 315, 333, 368, 534-548), `src/CV_model_gurobi_fixed.py` (çoklu satır: 184-190, 222, 242, 273, 415-422).

## Sapma notu (önemli)

Kullanıcının F-listesinde önerdiği formül şuydu: `M_ij = max(0, lc[i] + st[i] + break + tt[i,j] - ec[j])`. Bu formüldeki **`-ec[j]` terimi kullanılmadı**. Gerekçe: [[karar_a4_zaman_penceresi_bigm_kosullandirma]] (A4) sonrasında `c18_lb` koşullu hale geldiğinden `tau[j,t]`'nin (varış zamanı) alt sınırı artık `ec[j]` (düğümün en erken tamamlanma zamanı) değil, **0**. Eğer `-ec[j]` terimi formüle olduğu gibi dahil edilseydi, M değeri gerçekte gerekenden daha küçük çıkacak ve bazı feasible çözümleri (özellikle `tau[j,t]` gerçekten 0'a yakın olduğu durumlarda) kesecekti — yani formül A4 öncesi varsayımlarla (koşulsuz `c18_lb`, `ec[j]` alt sınır garantisi) tutarlıydı ama A4 sonrası model için artık geçerli değildi. Bu yüzden `-ec[j]` terimi düşürülüp M, `ec[j]`'yi varsaymayan bir üst sınırla türetildi.

## Doğrulama

Modelde `|katsayı| >= 99999` olan terim sayısı: **0** (öncesinde `100000.0` kullanan onlarca terim vardı). R5 problem setinde Gurobi 13 ile OPTIMAL çözüm (EV: `obj=10116.10`, CV: `obj=10116.10`).

## Sources

- `src/EV_v_1_1_fixed.py` (çoklu satır: 272-283, 315, 333, 368, 534-548)
- `src/CV_model_gurobi_fixed.py` (çoklu satır: 184-190, 222, 242, 273, 415-422)
- `raw/CV_model_gurobi_exact.py` (orijinal sabit `100000.0`)
- `raw/EV_v.1.1.py` (orijinal sabit `100000.0`)

## Related

- [[karar_tight_big_m_gecisi_plani]]
- [[tight_big_m]]
- [[parametre_big_m_100000]]
- [[karar_a4_zaman_penceresi_bigm_kosullandirma]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
