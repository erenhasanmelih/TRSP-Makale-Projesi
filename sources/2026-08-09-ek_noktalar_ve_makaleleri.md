---
title: Ek Noktalar ve Makaleleri
tags: [yönerge, literatür, meta-sezgisel, atıf]
source: raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx
date: 2026-08-09
status: güncel
---

# Ek Noktalar ve Makaleleri

## Amaç

TRSP makalesinin farklı alt problemleri (rotalama, iş çizelgeleme, teknisyen çizelgeleme, teknisyen-araç uyumluluğu) için literatürden örnek makaleler ve bu makalelerde kullanılan yöntemleri eşleştirmek.

## Ne yapıldı

Belge 4 kategori altında 7 örnek makale ve kullandıkları yöntemleri listeliyor:

1. **Rotalama (VRP) için 2 örnek:**
   - *A RL-Based Solution for the CEVRP from the Last-Mile Delivery Perspective* → **Q-Learning** tabanlı meta-sezgisel; kesin yöntemlerin saatler sürdüğü büyük ölçekli EV rotalama problemlerini saniyeler içinde çözmek için.
   - *An Integrated Inventory-Routing System for Multi-item Joint Replenishment* → Açgözlü (Greedy) yapıcı sezgiseller + **VLSN (Very Large-Scale Neighborhood Search)**.
2. **İş Çizelgeleme için 2 örnek:**
   - *A beam search-based algorithm... for flexible manufacturing systems* → **Filtered Beam Search**.
   - *Stochastic mixed-model assembly line sequencing problem* → **Q-Learning** ile yönlendirilen **Hyper Simulated Annealing (HSA)**.
3. **Teknisyen Çizelgeleme için 2 örnek:**
   - *Stochastic skill-based manpower allocation in a cellular manufacturing system* → Hiyerarşik (4 aşamalı) sezgisel yaklaşım + IID örnekleme.
   - Kendi taslak metnindeki TRSP çalışması → **ALNS (Adaptive Large Neighborhood Search)** + Sweep melez mimarisi.
4. **Teknisyen-Araç Uyumluluğu için 1 örnek:**
   - *Multi-Depot General Colored TSP with Time Windows in Home Healthcare* → **VND** + "Bölme (Splitting)" prosedürü; "Renkler (Colors)" ve "Uyumluluk Matrisi" ile araç-hasta eşleşmesi modelleniyor — TRSP'deki teknisyen-araç uyumluluğu mantığıyla birebir örtüşüyor.

## Anahtar noktalar

- Colored TSP makalesi (Multi-Depot General Colored TSP with Time Windows), projenin "uyumluluk matrisi" ihtiyacı için doğrudan literatür temeli sağlıyor.
- Q-Learning literatürde hem rotalama hem çizelgeleme tarafında (iki farklı makalede) kullanılmış — projenin Q-Learning + VND melez tercihini destekliyor.
- MTZ (Miller-Tucker-Zemlin) burada doğrudan geçmiyor ama "kodda ve matematiksel modeldeki farklılıklar" ve "makale adımlar" belgelerinde alt-tur önleme bağlamında geçiyor.

## Kararlar

- [[karar_literatur_temelli_problem_tanimi_md_gctsp_tw]]

## Açık konular

- ALNS ve VND'nin bu projede birlikte mi yoksa VND'nin tek başına mı kullanılacağı netleşmemiş — "makale adımlar ve düzenlemeler" belgesinde nihai mimari VND + Q-Learning olarak seçilmiş, ALNS örnek literatür referansı olarak kalıyor.

## Sources

- `raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx` (tam metin)

## Related

- [[colored_tsp]]
- [[q_learning]]
- [[vnd]]
- [[literatur_alternatif_metasezgiseller]]
- [[uyumluluk_matrisi]]
