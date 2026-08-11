---
title: Karar (Planlı) — Hibrit Algoritma Mimarisinin Geliştirme Sırası
tags: [karar, planlı, hibrit-algoritma, mimari, kritik]
source: raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Karar (Planlı) — Hibrit Algoritma Mimarisinin Geliştirme Sırası

## Karar

Büyük ölçekli problemler (50-100 müşteri) için "Q-Öğrenme Destekli Melez VND" algoritması aşağıdaki sırayla inşa edilecek ve kodlanacak:

1. **Veri Ön İşleme ve Kümeleme:** [[catboost]] + [[topsis]] modülleriyle aciliyet ve teknisyen yetkinliğine göre düğümler alt kümelere ayrılır.
2. **Başlangıç Çözümü Üretimi (Warm-Start):** basit sezgisellerle (Sweep) hızlı ve geçerli başlangıç rotaları üretilir — bkz. [[warm_start]].
3. **Yerel Kesin Çözümler:** küçük kümeler (5-7 müşteri) Gurobi'ye (Branch-and-Bound) gönderilir, alt bölgelerin yerel optimum rotaları kesin olarak bulunur.
4. **Gelişmiş Meta-Sezgisel Arama (VND):** alt rotalar birleştirildikten sonra [[vnd]] devreye girer — Swap, Insert, Reverse, Drop/Add operatörleri; k-drop/add sarsma (shaking) mekanizmasıyla yerel optimuma takılmayı önler; hangi operatörün seçileceğine [[q_learning]] karar verir (Yıldız vd., 2025).

## Gerekçe

Devasa arama uzayını doğrudan taramak yerine, önce kümeleme + warm-start ile arama uzayını daraltmak, sonra küçük kümelerde kesin çözüm bulmak, son olarak meta-sezgisel ile global iyileştirme yapmak — hem hız hem çözüm kalitesi dengesini hedefliyor.

## Kapsam / Faz

Faz 2 (Sezgisel Kodun Yazılması) kapsamında planlanıyor; henüz kodda uygulanmamış.

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[catboost]]
- [[topsis]]
- [[warm_start]]
- [[vnd]]
- [[q_learning]]
- [[gurobi_mip_cozucusu]]
- [[karar_3_fazli_uygulama_yol_haritasi]]
