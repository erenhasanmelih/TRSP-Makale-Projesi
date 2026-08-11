---
title: Karar (Planlı) — İptal Olasılığına Dayalı Ön Filtreleme
tags: [karar, planlı, makine-öğrenmesi, ön-filtreleme]
source: raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx
date: 2026-08-09
status: güncel
---

# Karar (Planlı) — İptal Olasılığına Dayalı Ön Filtreleme

## Karar

CatBoost ile her iş emri için 0-1 arası bir iptal olasılık skoru hesaplanacak; bu, Gurobi modeline veri beslenmeden önce bir ön işleme filtresi olarak çalışacak. Skoru %80 üzerinde olan iş emirleri optimizasyona hiç sokulmayacak; daha düşük riskli ama şüpheli olanlar TOPSIS ile ağırlıklandırılıp "düşük öncelikli" olarak rotanın sonuna eklenecek.

## Gerekçe

İptal riski yüksek görevlere kaynak ayrılmasını önleyerek karbon emisyonu israfını azaltmak; Gurobi'nin arama uzayını gereksiz iş emirlerinden arındırarak çözüm süresini hızlandırmak.

## Sources

- `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx`

## Related

- [[iptal_olasiligi_tahmini]]
- [[catboost]]
- [[topsis]]
- [[karar_3_asamali_rolling_horizon_sistem_mimarisi]]
