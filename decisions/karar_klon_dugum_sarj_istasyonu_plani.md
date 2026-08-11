---
title: Karar (Planlı) — Şarj İstasyonları İçin Klon Düğüm Üretimi
tags: [karar, planlı, ev, şarj-istasyonu, matematiksel-model]
source: raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Karar (Planlı) — Şarj İstasyonları İçin Klon Düğüm Üretimi

## Karar

Matematiksel modelin şarj istasyonları için "klonlanmış" (dummy) düğümler üretmesi ve bunlara giriş-çıkış akışlarını tanımlaması gerekiyor — EV'ler rotanın ortasında bir şarj istasyonuna birden fazla kez uğrayabilmeli.

## Gerekçe

Kısmi şarj (partial recharging) esnekliğinin anlamlı olabilmesi için EV'nin aynı istasyona birden fazla kez dönebilmesi gerekiyor; mevcut modelde/kodda bu klonlama yapısı yok.

## Sources

- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[klon_dugum_node_replication]]
- [[partial_recharging]]
- [[karar_partial_charging_denklemleri_entegrasyonu_plani]]
- [[sorun_sarj_yakit_istasyonlari_kodda_yok]]
