---
title: Parametre — Big-M (100000.0)
tags: [entity, parametre, big-m, gurobi]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Parametre — Big-M (100000.0)

Her iki dosyada da sabit `100000.0` değeri, koşullu kısıtları (bir ikili değişken 0/1 olduğunda kısıtı aktif/pasif kılmak için) ifade etmede kullanılıyor. Kullanıldığı yerler:

- `c8_zaman_ilerleme`: zaman ilerlemesi kısıtı (CV: satır 83, EV: satır 172).
- `mola_yoksa_erken_donus`: erken dönüş kısıtı (CV: 105, EV: 192).
- `mola_baslama_alt/ust_sinir`: mola başlama zaman aralığı (CV: 119,123, EV: 204,208).
- `c_full_depot_ub/lb`: depo çıkışında tam dolum kısıtları (CV: 189,193, EV: 373,377).
- `lc0 = 100000.0`: CV `__main__` bloğunda ayrı bir "büyük sayı" olarak da tanımlı (satır 381) ama `build_model` içinde kullanılmıyor.

Bu, projenin [[tight_big_m]] planının hedefidir — tüm bu sabit `100000.0` değerlerinin dinamik, duruma özgü (zaman penceresi farkına dayalı) değerlerle değiştirilmesi planlanıyor (bkz. [[karar_tight_big_m_gecisi_plani]]).

## Güncelleme (Faz 2, 2026-08-11)

**`raw/`'da hâlâ sabit `100000.0` var** (Hard Rule 1 gereği hiç dokunulmadı, yukarıdaki satır referansları hâlâ geçerli). Ama `src/CV_model_gurobi_fixed.py` ve `src/EV_v_1_1_fixed.py`'de bu sabitler **tight/dinamik M formülleriyle** değiştirildi:

- `c8` zaman ilerlemesi: `M8 = tau_ub[i] + st[i] + break_duration (+ istasyonsa şarj süresi üst sınırı)` (`src/CV_model_gurobi_fixed.py:184-190`, `src/EV_v_1_1_fixed.py:272-283`).
- Molasız erken dönüş: `M = max(0, tau_ub[i]+st[i]+tt[i,0]-break_max)` (`CV:222`, `EV:315`).
- Mola başlama üst sınırı: `M = max(0, tau_ub[i]+st[i]-break_max)` (`CV:242`, `EV:333`).
- `c16/c17/c18` zaman penceresi (A4 ile birlikte koşullandırıldı): bkz. [[karar_a4_zaman_penceresi_bigm_kosullandirma]].
- `c20/c21`, `c_full_depot_lb/ub` (A2+C1 ile birlikte, artık `k` = birleşik (araç,ekip) indeksine göre): `Q_of_k[k]`/`G_of_k[k]` tabanlı, bkz. [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]].

Sabit `lc0=100000.0` (CV `__main__`) yerine `tau_ub[i]` artık istasyon/depo düğümlerinde `horizon_end`'e (vardiya ufku) sınırlandı — bu, `parametre_big_m_100000` kapsamının biraz dışında ama ilgili bir sapma, bkz. [[sorun_tau_ub_istasyon_depo_ufuk_sapmasi]].

Tam uygulama kaydı ve sapma notu (kullanıcının `-ec[j]` önerisinin neden kullanılmadığı dahil): [[karar_c2_tight_big_m_uygulamasi]]. Doğrulama: modelde `|katsayı|>=99999` olan terim sayısı 0 (öncesinde çoktu). R5'te Gurobi 13 ile OPTIMAL (EV/CV obj=10116.10).

## Sources

- `raw/CV_model_gurobi_exact.py` (çoklu satır: 83, 105, 119, 123, 189, 193, 381)
- `raw/EV_v.1.1.py` (çoklu satır: 172, 192, 204, 208, 373, 377)
- `src/CV_model_gurobi_fixed.py` (çoklu satır: 184-190, 222, 242, 273)
- `src/EV_v_1_1_fixed.py` (çoklu satır: 272-283, 315, 333, 368)

## Related

- [[tight_big_m]]
- [[karar_tight_big_m_gecisi_plani]]
- [[gurobi_mip_cozucusu]]
- [[karar_c2_tight_big_m_uygulamasi]]
- [[karar_a4_zaman_penceresi_bigm_kosullandirma]]
- [[sorun_tau_ub_istasyon_depo_ufuk_sapmasi]]
