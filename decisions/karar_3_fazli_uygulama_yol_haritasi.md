---
title: Karar — 3 Fazlı Uygulama Yol Haritası
tags: [karar, proje-planı, faz, yol-haritası]
source: raw/Yönergelerimiz/Full Path.docx
date: 2026-08-09
status: güncel
---

# Karar — 3 Fazlı Uygulama Yol Haritası

## Karar

Tüm plan (matematiksel model revizyonu, çizelgeleme eklentisi, hibrit algoritma, Pareto analizi) 3 fazda uygulanacak:

1. **Faz 1 — Kod Revizyonu:** `CV_model_gurobi_exact.py`, [[karar_4b_to_3b_index_reduction_plani|indis düşürme]] ve [[karar_tight_big_m_gecisi_plani|tight Big-M]]'e göre yeniden yazılacak; 10-15 düğümlük sorunun ortadan kalkması ve Gurobi'nin hızlanması beklenecek.
2. **Faz 2 — Sezgisel Kodun Yazılması:** büyük veriler (50-100 düğüm) için Q-Learning + VND tabanlı melez meta-sezgisel kodlanacak (bkz. [[karar_hibrit_algoritma_mimari_sirasi]]).
3. **Faz 3 — Word Taslağının Doldurulması:** kodlar çalışıp sonuçlar (tablo, grafik) alındıktan sonra, Word belgesindeki eksik başlıklar (özellikle 4.11, 4.6 ve Matematiksel Model) akademik atıflarla doldurulacak.

## Gerekçe

Önce çözücü performansını (Faz 1) düzeltmeden büyük ölçekli sezgisel geliştirmenin (Faz 2) test edilmesi güç; sonuçlar netleşmeden makale metninin (Faz 3) yazılması erken olur — sıralama bağımlılığı bilinçli.

## Sources

- `raw/Yönergelerimiz/Full Path.docx`

## Related

- [[karar_4b_to_3b_index_reduction_plani]]
- [[karar_tight_big_m_gecisi_plani]]
- [[karar_hibrit_algoritma_mimari_sirasi]]
- [[karar_pareto_epsilon_constraint_plani]]
