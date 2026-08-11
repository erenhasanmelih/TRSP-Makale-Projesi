---
title: Karar (Kod, EV) — Feasibility-Odaklı Gurobi Tuning ve IIS Diagnostik
tags: [karar, kod, ev, gurobi-tuning, diagnostik]
source: raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Karar (Kod, EV) — Feasibility-Odaklı Gurobi Tuning ve IIS Diagnostik

## Karar

`FEASIBILITY_FOCUSED_PARAMS=True` olduğunda (satır 741-755), EV modeli 12 Gurobi parametresini feasibility bulmaya odaklı ayarlıyor: `MIPFocus=2` (optimallik kanıtından çok iyi çözüm bulmaya odaklan), `Heuristics=0.15`, `NoRelHeurTime=600`, `NoRelHeurSolutions=5`, `RINS=25`, `SubMIPNodes=500`, `Presolve=2`, `Symmetry=2`, `MIPSepCuts=2`, `Cuts=2`, `IntegralityFocus=1`, `NumericFocus=1`, `MIPGap=0.005`. Model `INFEASIBLE` sonucu dönerse, `computeIIS()` çağrılıp çakışan kısıt alt kümesi `.ilp` dosyasına yazılıyor (satır 759-764).

## Gerekçe (çıkarım)

Bu, [[karar_tight_big_m_gecisi_plani]] ve [[karar_4b_to_3b_index_reduction_plani]]'nda planlanan **yapısal** (matematiksel model seviyesi) düzeltmelerden farklı, **pratik/geçici bir çözücü ayarı** yaklaşımı — EV modelinin zorluğuna karşı mevcut haliyle mücadele etmek için devreye sokulmuş. `MODEL_TIME_LIMIT_SECONDS=3600`'ün CV'nin 900 saniyesinden 4 kat uzun olmasıyla tutarlı (bkz. [[model_calistirma_parametreleri_ev]]).

## İlişki

Bu karar, yapısal düzeltmelerin (index reduction, tight Big-M) henüz uygulanmadığı bir ara dönemde, EV modelinin en azından bir çözüm üretebilmesi için alınmış bir "workaround" gibi görünüyor — planlı revizyonlar tamamlandığında bu tuning parametrelerinin gerekliliği yeniden değerlendirilmeli.

## Sources

- `raw/EV_v.1.1.py:741-770`

## Related

- [[model_calistirma_parametreleri_ev]]
- [[karar_tight_big_m_gecisi_plani]]
- [[karar_4b_to_3b_index_reduction_plani]]
- [[gurobi_mip_cozucusu]]
