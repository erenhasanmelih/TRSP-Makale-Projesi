---
title: Karar (Faz 2, A2+C1) — Birleşik k İndeksi ve Enerji/Yakıt İzlemenin Çok-İndisli Hale Getirilmesi
tags: [karar, faz2, mip-boyut-küçültme, a2, c1, a5, en-riskli-degisiklik]
source: src/EV_v_1_1_fixed.py; src/CV_model_gurobi_fixed.py
date: 2026-08-11
status: güncel
---

# Karar (Faz 2, A2+C1) — Birleşik k İndeksi ve Enerji/Yakıt İzlemenin Çok-İndisli Hale Getirilmesi

## Kapsam

Bu, Faz 2'nin **en riskli ve en kapsamlı** değişikliğidir — hem C1 (4B→3B index reduction) hem A2 (heterojen filo desteği) hem A5 (yetkinlik filtresi) aynı refaktörde birlikte ele alındı, çünkü üçü de aynı temel veri yapısına (`x`'in indeksleme şeması) dokunuyor.

## Karar

`x[i,j,v,t]` (4 boyutlu: çıkış, varış, araç, ekip) → `x[i,j,k]` (3 boyutlu), burada `k` = `(araç, ekip)` **birleşik indeksi**:

```python
K_pairs = [(v, t) for v in V for t in T]
KK = list(range(len(K_pairs)))
k_veh = {k: K_pairs[k][0] for k in KK}
k_crew = {k: K_pairs[k][1] for k in KK}
```

(EV: `src/EV_v_1_1_fixed.py:118-121`, CV: `src/CV_model_gurobi_fixed.py:37-40` — CV'de değişken adı `kk` kullanılıyor, bkz. aşağıdaki "Beklenmeyen zorluklar".)

**A5 (yetkinlik filtresi)** aynı refaktörle uygulandı: `_crew_allowed(node, t)` fonksiyonu, uyumsuz (düğüm, ekip) çiftlerini eleyerek geçerli arc-k kombinasyonlarını (`arc_ks`) üretiyor — uyumsuz `x` hiç üretilmiyor (doğrulama: 0 adet uyumsuz `x`).

**Enerji/yakıt izleme (`ye/YE`, `yc/YC`) artık `(Np, K)` çok-indisli:** önceden düğüm-bazlı tek bir değer tutan bu değişkenler artık her (düğüm, k) çifti için ayrı — bu, **A2'nin (heterojen filo)** ön koşuludur: `Q_of_k[k]`/`G_of_k[k]` (araç-bazlı kapasite) ve `he_of_k[k]`/`hc_of_k[k]` (araç-bazlı tüketim oranı, bkz. [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]) sayesinde artık farklı araç tipleri doğru şekilde modelleniyor.

## Konum (refaktörün dokunduğu yerler)

- **EV:** `src/EV_v_1_1_fixed.py:113-206` (temel indeks kurulumu) + amaç fonksiyonu, `c2-c6`, `c8`, mola kısıtları, `c16-c18`, non-overlap, `c20-c22`, raporlama fonksiyonlarının **tamamı** yeni indekse göre güncellendi.
- **CV:** `src/CV_model_gurobi_fixed.py:32-116` (temel indeks kurulumu) + aynı kısıt gruplarının tamamı.

## Ölçüm

| Metrik | EV öncesi | EV sonrası | CV öncesi | CV sonrası |
|---|---|---|---|---|
| `\|x\|` | 5670 | 2604 (-%54) | 900 | 198 (-%78) |
| Toplam kısıt | — | -%47 (ortalama) | — | -%47 (ortalama) |

R5 problem setinde Gurobi 13 ile her iki model de OPTIMAL, `obj=10116.10` (EV=CV, tutarlılık doğrulaması).

## Beklenmeyen zorluklar

**CV'de isim çakışması (`k`):** `CV_model_gurobi_exact.py`'nin orijinal parametre listesinde `k` zaten bir talep (demand) parametresi olarak kullanılıyordu. Yeni birleşik (araç,ekip) indeksi de doğal olarak `k` adını istiyordu. Çözüm: fonksiyon girişinde `k_demand = k; del k` (satır 24-26) ile eski `k` parametresi `k_demand` adına taşınıp orijinal isim serbest bırakıldı, ardından yeni birleşik indeks için tüm CV kodunda `kk` değişken adı kullanıldı (`K_pairs`, `KK`, `k_veh[kk]` vb. — EV'deki `k` ile aynı anlama geliyor, sadece isim farklı). Küçük ama gerçek bir gotcha; ileride CV/EV kodlarını birleştirme ihtimali varsa bu isimlendirme farkı (`k` vs `kk`) hatırlanmalı.

## Çapraz referanslar

- Plan sayfası (C1): [[karar_4b_to_3b_index_reduction_plani]]
- Kavram sayfaları: [[colored_tsp]], [[index_reduction_3b]], [[uyumluluk_matrisi]]
- Değişken sayfaları: [[degisken_x_arc_tahsisi]], [[degisken_yakit_enerji_izleme]]
- Yardımcı veri yapıları: [[birlesik_k_indeksi_ve_yardimci_haritalar]]
- İlişkili A7 (araç-bazlı tüketim oranı): [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]

## Sources

- `src/EV_v_1_1_fixed.py:113-206`
- `src/CV_model_gurobi_fixed.py:24-26,32-116`
- `raw/EV_v.1.1.py:95-99` (orijinal 4B x, düğüm-bazlı ye/YE)
- `raw/CV_model_gurobi_exact.py:21,24-25` (orijinal 4B x, düğüm-bazlı yc/YC, orijinal `k` talep parametresi)

## Related

- [[karar_4b_to_3b_index_reduction_plani]]
- [[colored_tsp]]
- [[index_reduction_3b]]
- [[uyumluluk_matrisi]]
- [[degisken_x_arc_tahsisi]]
- [[degisken_yakit_enerji_izleme]]
- [[birlesik_k_indeksi_ve_yardimci_haritalar]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
- [[karar_c2_tight_big_m_uygulamasi]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
