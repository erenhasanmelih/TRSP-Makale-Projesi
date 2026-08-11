---
title: Karar (Planlı) — 4B'den 3B'ye İndis Düşürme
tags: [karar, planlı, matematiksel-model, mip-boyut-küçültme]
source: raw/Yönergelerimiz/Full Path.docx
date: 2026-08-09
status: güncel
---

# Karar (Planlı) — 4B'den 3B'ye İndis Düşürme

## Karar

Mevcut 4 boyutlu karar değişkeni **x(çıkış, varış, araç, ekip)**, [[colored_tsp]] mantığı (Acar ve Altın, 2025) kullanılarak 3 boyutlu **x(çıkış, varış, uyumlu araç-ekip kaynağı)**'a indirgenecek. Araç ve ekip önceden eşleştirilecek (statik eşleştirme varsayımı).

## Gerekçe

Gurobi modelinin 10-13 düğümde tıkanmasının bir nedeni olarak karar değişkeni sayısının fazlalığı görülüyor; boyut indirgeme, çözüm uzayını daraltarak Branch-and-Bound performansını artırması bekleniyor.

## Kapsam / Faz

Faz 1 (Kod Revizyonu) kapsamında, sadece `CV_model_gurobi_exact.py` için planlanmış.

## Bilinen risk / açık konu

Statik araç-ekip eşleştirme varsayımı, kodun mevcut dinamik ekip oluşturma yaklaşımıyla (bkz. [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]) çelişebilir — henüz uygulama detayı belirsiz.

## Uygulama (Faz 2, 2026-08-11)

**Bu plan artık uygulandı.** `raw/` DEĞİŞTİRİLMEDEN, `src/EV_v_1_1_fixed.py` ve `src/CV_model_gurobi_fixed.py` içinde `x[i,j,v,t]` (4B) → `x[i,j,k]` (3B) indirgemesi yapıldı — burada `k`, plandaki gibi statik bir "önceden eşleştirme" değil, **tüm olası (araç, ekip) çiftlerinin birleşik listesi** (`K_pairs = [(v,t) for v in V for t in T]`, `KK = range(len(K_pairs))`) olarak kuruldu. Yani "araç-ekip önceden eşleştirilecek" varsayımı gerçekleşmedi — bunun yerine plan sayfasının kendi işaret ettiği risk (dinamik ekip oluşturmayla çelişme, bkz. yukarıdaki "Bilinen risk") **çözüldü**: `K_pairs` her (araç, ekip) kombinasyonunu ayrı bir `k` olarak tutuyor, uyumsuz kombinasyonlar `_crew_allowed()` yetkinlik filtresiyle (A5, aynı refaktörle birlikte uygulandı — bkz. [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]) elenip `x`'ten hiç üretilmiyor.

Ölçülen etki: EV `|x|` 5670→2604 (-%54), CV `|x|` 900→198 (-%78); toplam kısıt sayısında EV/CV ortalaması -%47. R5 problem setinde Gurobi 13 ile OPTIMAL çözüm alındı (EV: obj=10116.10, CV: obj=10116.10).

Detaylı uygulama kaydı: [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]] (bu sayfa, index reduction'ı A5 yetkinlik filtresi ve enerji izleme değişkenlerinin çok-indisli hale getirilmesiyle birlikte tek bir refaktör olarak ele alıyor). Kod haritası ve `raw/` izolasyon gerekçesi: [[karar_src_klasoru_ve_raw_izolasyonu]].

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `src/EV_v_1_1_fixed.py:113-206`
- `src/CV_model_gurobi_fixed.py:32-116`

## Related

- [[index_reduction_3b]]
- [[colored_tsp]]
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]
- [[karar_3_fazli_uygulama_yol_haritasi]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
- [[sources/2026-08-09-full_path]]
