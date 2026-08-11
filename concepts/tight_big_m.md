---
title: Big-M Tightening (Sıkı Big-M)
tags: [kavram, matematiksel-model, mip, big-m]
source: raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Big-M Tightening (Sıkı Big-M)

MIP modellerinde koşullu kısıtları (bir ikili değişken 0 veya 1 olduğunda kısıtı aktif/pasif yapmak için) ifade etmek için kullanılan Big-M sabitinin, mümkün olan en küçük geçerli değere indirgenmesi tekniği. Gevşek (çok büyük) Big-M değerleri, Branch-and-Bound ağacının etkin budama (pruning) yapmasını engeller ve çözüm süresini ciddi şekilde uzatır.

## TRSP projesindeki durum

- Mevcut kodda (`CV_model_gurobi_exact.py`, `EV_v.1.1.py`) zaman ilerlemesi ve dönüş kısıtlarında sabit `100000.0` kullanılıyor.
- Cordeau vd. (2002)'ye atıfla, bu sabit değerin dinamik olarak müşterilerin zaman pencereleri arasındaki farka göre hesaplanması planlanıyor.
- "Makale adımlar ve düzenlemeler" belgesi ek olarak Big-M'in "her teknisyenin o günkü maksimum mesai bitiş süresi" ile sınırlandırılmasını, ve MTZ (Miller-Tucker-Zemlin) alt-tur önleme kısıtlarının bu sıkılaştırmayla birlikte ele alınmasını öneriyor.

## Amaç

Gurobi modelinin 10-13 düğümde tıkanmasının ana nedenlerinden biri olarak teşhis ediliyor; sıkılaştırma ile Branch-and-Bound performansının önemli ölçüde artması bekleniyor.

## Uygulama (Faz 2, 2026-08-11)

Bu teknik `src/CV_model_gurobi_fixed.py` ve `src/EV_v_1_1_fixed.py`'de uygulandı (C2) — `raw/` değişmedi. 4 kısıt grubunda (`c8` zaman ilerlemesi, mola başlama alt/üst sınır, molasız erken dönüş, `c_full_depot_lb/ub`, `c20/c21`) zaman penceresi farkından türetilen M değerleri sabit `100000.0`'ın yerini aldı. Doğrulama: modelde `|katsayı|>=99999` terim sayısı 0 (öncesinde çoktu). Detay ve sapma notu (kullanıcının `-ec[j]` içeren formülünün neden tam kullanılmadığı): [[karar_c2_tight_big_m_uygulamasi]]. Parametrenin kendi sayfası: [[parametre_big_m_100000]].

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`
- `src/CV_model_gurobi_fixed.py`
- `src/EV_v_1_1_fixed.py`

## Related

- [[karar_tight_big_m_gecisi_plani]]
- [[gurobi_mip_cozucusu]]
- [[literatur_alternatif_metasezgiseller]]
- [[model_karar_degiskenleri_ve_parametreleri]]
- [[karar_c2_tight_big_m_uygulamasi]]
- [[parametre_big_m_100000]]
