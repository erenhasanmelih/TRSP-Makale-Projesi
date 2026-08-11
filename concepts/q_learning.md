---
title: Q-Learning
tags: [kavram, pekiştirmeli-öğrenme, meta-sezgisel, hibrit-algoritma]
source: raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx; raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Q-Learning

Pekiştirmeli öğrenme (reinforcement learning) tabanlı bir meta-sezgisel/karar mekanizması. TRSP projesinde planlanan Q-Learning + VND melez algoritmasının öğrenme bileşenidir.

## Literatürdeki örnekler

- *A Reinforcement Learning-Based Solution for the Capacitated Electric Vehicle Routing Problem* — Q-Learning, kapasite kısıtlı EV rotalama problemini (CEVRP) kesin yöntemlerin saatler sürdüğü büyük ölçekli ağlarda saniyeler içinde çözmek için kullanılıyor.
- *Stochastic mixed-model assembly line sequencing problem* — Q-Learning, Hiper Benzetimli Tavlama (HSA) meta-sezgiselini yönlendiriyor; stokastik işlem süreleri altında montaj hattı sıralamasını optimize ediyor.

## TRSP projesindeki planlanan rolü

Yıldız vd. (2025)'e atıfla, VND algoritmasının hangi komşuluk operatörünü (Swap, Insert, Reverse, Drop/Add) seçeceğine Q-Learning karar verecek — böylece algoritma saniyeler içinde en iyi rotayı "öğrenerek" bulacak (bkz. [[karar_hibrit_algoritma_mimari_sirasi]]).

## Durum

Henüz kodda uygulanmamış; Faz 2 (Full Path.docx — "Sezgisel Kodun Yazılması") kapsamında planlanıyor.

## Sources

- `raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx`
- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[vnd]]
- [[karar_hibrit_algoritma_mimari_sirasi]]
- [[literatur_alternatif_metasezgiseller]]
- [[warm_start]]
