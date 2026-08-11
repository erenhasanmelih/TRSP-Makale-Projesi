---
title: Karar Değişkeni — x[i,j,v,t] (Arc Tahsisi)
tags: [entity, karar-değişkeni, gurobi, rotalama]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Karar Değişkeni — x[i,j,v,t]

Modelin ana ikili (binary) karar değişkeni: `x[i,j,v,t] = 1` ⟺ araç `v`, ekip `t` ile `i` düğümünden `j` düğümüne gidiyor.

```python
x = m.addVars(A, V, T, vtype=GRB.BINARY, name="x")
```

- `A`: geçerli arc'lar (yay) kümesi.
- `V`: araç kümesi.
- `T`: ekip (crew) kümesi — hem CV hem EV'de bireysel teknisyenleri ve `itertools.combinations` ile oluşturulan ikili ekipleri içerir (bkz. [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]).

4 boyutlu bu yapı, [[karar_4b_to_3b_index_reduction_plani]]'nda 3 boyuta (araç-ekip önceden eşleştirilerek) indirgenmesi planlanan tam da bu değişken.

CV: `CV_model_gurobi_exact.py:21`. EV: `EV_v.1.1.py:95`.

## Güncelleme (Faz 2, 2026-08-11)

**`raw/`'da hâlâ 4 boyutlu** — `x[i,j,v,t]` yukarıdaki tanımıyla değişmedi (Hard Rule 1). Ama `src/CV_model_gurobi_fixed.py` ve `src/EV_v_1_1_fixed.py`'de artık **3 boyutlu**: `x[i,j,k]`, burada `k` araç ve ekibin birleşik indeksi (`K_pairs = [(v,t) for v in V for t in T]`, `k_veh[k]`/`k_crew[k]` ile ayrıştırılıyor). Bu, [[karar_4b_to_3b_index_reduction_plani]]'nın planladığı indirgemenin gerçekleşmiş hâli — ama plan "statik önceden eşleştirme" öngörüyordu, uygulanan çözüm bunun yerine **tüm (araç,ekip) çiftlerini** `K_pairs`'te tutup uyumsuzları `_crew_allowed()` filtresiyle eliyor (A5 yetkinlik kısıtı aynı refaktörle geldi).

Ölçülen etki (R5 problem seti): EV `|x|` 5670→2604 (-%54), CV `|x|` 900→198 (-%78). Tam uygulama kaydı: [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]. Yardımcı veri yapıları (`K_pairs`, `KK`, `XK`, `Q_of_k`, `G_of_k` vb.): [[birlesik_k_indeksi_ve_yardimci_haritalar]].

## Sources

- `raw/CV_model_gurobi_exact.py:21`
- `raw/EV_v.1.1.py:95`
- `src/CV_model_gurobi_fixed.py:37-64`
- `src/EV_v_1_1_fixed.py:113-145`

## Related

- [[karar_4b_to_3b_index_reduction_plani]]
- [[index_reduction_3b]]
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]
- [[model_karar_degiskenleri_ve_parametreleri]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
- [[birlesik_k_indeksi_ve_yardimci_haritalar]]
