---
title: Karar (Planlı) — 3 Aşamalı Rolling Horizon Sistem Mimarisi
tags: [karar, planlı, sistem-mimarisi, rolling-horizon, çizelgeleme]
source: raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx
date: 2026-08-09
status: güncel
---

# Karar (Planlı) — 3 Aşamalı Rolling Horizon Sistem Mimarisi

## Karar

TRSP planlama sistemi 3 aşamada kurgulanacak:

1. **Haftalık Çizelgeleme (Taktiksel/Makro):** CatBoost ile talep tahmini, vardiya/kapasite planlaması, TOPSIS ile teknisyen sıralaması.
2. **Günlük Atama ve Rotalama (Operasyonel/Mikro):** Window-Wise Sweep ile warm-start, Python+Gurobi ile kesin atama, gün içi dinamik revizyon.
3. **Sistem Entegrasyonu (Rolling Horizon):** haftalık ve günlük seviyelerin kopuk çalışmaması için günlük operasyonel verilerin (gecikme, ertelenen iş, arıza) ertesi günün ve kalan haftanın planına geri bildirim olarak aktarılması.

## Gerekçe

Sahadaki belirsizlikleri (talep dalgalanması, iptaller, arızalar) yönetmek ve doğru yetkinlikteki kapasitenin doğru günlerde hazır olmasını sağlamak.

## Sources

- `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx`

## Related

- [[rolling_horizon]]
- [[warm_start]]
- [[karar_gunluk_haftalik_planlama_pool_plani]]
- [[karar_iptal_olasiligi_on_filtreleme_plani]]
