---
title: Gurobi (MIP Çözücüsü)
tags: [entity, çözücü, exact-yöntem, mip]
source: raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: taslak
---

# Gurobi (MIP Çözücüsü)

TRSP'nin tam (exact) matematiksel modelinin çözümü için kullanılan ticari Karma Tamsayılı Programlama (MIP) çözücüsü. Python tarafında [[python_gurobipy]] kütüphanesi üzerinden çağrılıyor.

## Bilinen sınırlar (yönerge belgelerinde tespit edilen)

- Mevcut model 10-13 (bazı belgelerde 10-15) düğümde tıkanıyor — Branch-and-Bound ağacının büyük Big-M değerleri ve gevşek alt-tur önleme kısıtları nedeniyle etkin budama yapamaması gösteriliyor (bkz. [[tight_big_m]]).
- Ghasemi Saghand et al. (2019) çalışmasına atıfla, kesin yöntemlerin karma tamsayılı problemlerdeki çözüm uzayı zorlukları makalede bu sınırlamayı literatürle temellendirmek için kullanılacak.
- Hibrit algoritma mimarisinde Gurobi/Branch-and-Bound, tüm problemi değil sadece küçük kümelenmiş alt bölgeleri (5-7 müşteri) kesin olarak çözmek için kullanılacak (bkz. [[karar_hibrit_algoritma_mimari_sirasi]]).

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`
- `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx`

## Related

- [[sorun_rc13_darbogaz_kok_neden_analizi]] (Symmetry=2 model boyutu indirimini modelleme düzeyinde ikame etmiyor; presolve yetkinlik filtresini bulamıyor)
- [[python_gurobipy]]
- [[tight_big_m]]
- [[index_reduction_3b]]
- [[karar_hibrit_algoritma_mimari_sirasi]]
- [[model_karar_degiskenleri_ve_parametreleri]]
