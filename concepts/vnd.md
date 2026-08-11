---
title: VND (Variable Neighborhood Descent / Değişken Komşuluk İnişi)
tags: [kavram, meta-sezgisel, yerel-arama, hibrit-algoritma]
source: raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx; raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# VND (Variable Neighborhood Descent / Değişken Komşuluk İnişi)

Birden fazla komşuluk yapısını sistematik olarak deneyerek yerel optimuma inen bir meta-sezgisel yerel arama tekniği. TRSP projesinde planlanan hibrit algoritmanın (Q-Learning + VND) temel iyileştirme bileşenidir.

## Literatür kaynağı

*Multi-Depot General Colored Traveling Salesman Problem with Time Windows in Home Healthcare System* — VND + "Bölme (Splitting)" prosedürü; [[colored_tsp]] ile birlikte kullanılıyor.

## TRSP projesindeki planlanan rolü

- Devasa iş listesi, araç kapasitesi ve zaman pencerelerine göre uygulanabilir rotalara "Bölünür" (Splitting), ardından VND ile rota içi iyileştirmeler (**Swap, Insert, Reverse, Drop/Add** operatörleri) yapılır.
- Yerel optimuma takılmamak için k-drop/add "sarsma" (shaking) mekanizması kullanılır.
- Hangi komşuluk operatörünün seçileceğine [[q_learning]] karar verir (Yıldız vd., 2025).
- Mimarideki sırası: Kümeleme (CatBoost/TOPSIS) → Warm-Start (Sweep) → Yerel Branch-and-Bound → **VND** (bkz. [[karar_hibrit_algoritma_mimari_sirasi]]).

## Durum

Henüz kodda uygulanmamış; Faz 2 kapsamında planlanıyor.

## Sources

- `raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx`
- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[q_learning]]
- [[colored_tsp]]
- [[karar_hibrit_algoritma_mimari_sirasi]]
- [[warm_start]]
