---
title: 3D Index Reduction (İndis Düşürme)
tags: [kavram, matematiksel-model, mip-boyut-küçültme]
source: raw/Yönergelerimiz/Full Path.docx
date: 2026-08-09
status: güncel
---

# 3D Index Reduction (İndis Düşürme)

Karar değişkeninin boyutunu azaltarak MIP modelinin çözüm uzayını küçültme tekniği. TRSP projesinde, mevcut 4 boyutlu karar değişkeni **x(çıkış, varış, araç, ekip)**'in, [[colored_tsp]] mantığı (Acar ve Altın, 2025) kullanılarak 3 boyutlu **x(çıkış, varış, uyumlu araç-ekip kaynağı)**'a indirgenmesi planlanıyor. Bunun ön koşulu, araç ve ekibin önceden eşleştirilmesidir (araç-ekip ikilisi tek bir "kaynak" indisi olarak ele alınır).

## Amaç

Gurobi modelinin 10-13 düğümde tıkanmasının bir nedeni olarak görülüyor — karar değişkeni sayısının (ve dolayısıyla Branch-and-Bound ağacının) büyüklüğünü azaltarak çözüm hızını artırmak hedefleniyor.

## Durum

**Faz 2'de (2026-08-11) uygulandı** — `raw/` değişmeden, `src/EV_v_1_1_fixed.py` ve `src/CV_model_gurobi_fixed.py`'de `x[i,j,v,t]`→`x[i,j,k]` indirgemesi yapıldı. Planlanan "araç-ekip önceden statik eşleştirme" yerine tüm (araç,ekip) çiftlerinin `K_pairs` listesi kuruldu ve `_crew_allowed()` yetkinlik filtresiyle uyumsuzlar elendi — bu, aşağıdaki "Bilinen risk" bölümünde işaretlenen gerilimi (statik eşleştirme vs dinamik ekip oluşturma) fiilen çözdü, çünkü hiçbir statik eşleştirme varsayımı yapılmadı. Ölçülen etki: EV `|x|` 5670→2604 (-%54), CV `|x|` 900→198 (-%78). Detay: [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]], plan sayfası: [[karar_4b_to_3b_index_reduction_plani]].

## Bilinen risk (lint-report-2026-08-09 X1 bulgusu, Faz 2'de çözüldü)

Önceden bu sayfa `karar_dinamik_teknisyen_ekibi_itertools_combinations` ile arasındaki gerilime (statik eşleştirme varsayımı vs kodun dinamik ekip oluşturması) değinmiyordu — bkz. [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]. Faz 2'nin uyguladığı çözüm (tüm çiftleri tutup filtrelemek) bu riski ortadan kaldırdı, ayrıntı için [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]'ye bakın.

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `src/EV_v_1_1_fixed.py:113-206`
- `src/CV_model_gurobi_fixed.py:32-116`

## Related

- [[colored_tsp]]
- [[karar_4b_to_3b_index_reduction_plani]]
- [[gurobi_mip_cozucusu]]
- [[model_karar_degiskenleri_ve_parametreleri]]
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
