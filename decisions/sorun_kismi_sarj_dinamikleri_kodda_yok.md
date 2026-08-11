---
title: Sorun — Kısmi Şarj (Partial Recharge) Dinamikleri Kodda Yok
tags: [sorun, ev, şarj-modeli, matematiksel-model-eksikliği]
source: raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Sorun — Kısmi Şarj (Partial Recharge) Dinamikleri Kodda Yok

## Sorun

Matematiksel model, şarj hızı katsayısı, maksimum şarj süresi ve dolum miktarının zaman ilerlemesine etkisini Kısıt (17) ve Kısıt (19) aracılığıyla hesaplıyor. Kodda bu tür bir dolum süresi hesabı yok; sadece aracın enerji seviyesi, tüketim katsayısı × mesafe çarpımıyla azaltılarak izleniyor.

Ayrıca "makale adımlar ve düzenlemeler.docx" bu eksikliği EV modelinin makale standardına göre "çalışamaz durumda" olmasının gerekçelerinden biri olarak gösteriyor: EV'ler bataryayı tam doldurmak zorunda değil, sadece bir sonraki müşteriye/depoya yetecek kadar şarj olabilmeli — kodda bu esneklik yok.

## ÇELİŞKİ (güncelleme — Stage 2 kod doğrulaması, 2026-08-09)

Bu iddia `EV_v.1.1.py` için **tam doğru değil**. Kodda `c8_zaman_ilerleme` kısıtına eklenmiş bir terim var (satır 165, 271): `charge_time_i = g_e * (YE[i] - ye[i]) if i in S_set else 0.0` — yani istasyonda geçirilen şarj süresi, şarj edilen miktarla (`YE[i]-ye[i]`, kısmi olabilir) orantılı olarak zaman eksenine ekleniyor. Bu, tam teşekküllü bir Keskin & Çatay (2016) formülasyonu olmayabilir (bu ingest bunu doğrulamadı) ama "kodda dolum süresi hesabı **yoktur**" iddiası artık geçerli değil — en azından EV modeli için kısmi bir mekanizma **var**. Muhtemelen docx, CV modelini (ki orada gerçekten hiç yok) veya EV'nin daha eski bir sürümünü tarif ediyor. Madde silinmiyor, bu nüansla birlikte tutuluyor.

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`
- `raw/EV_v.1.1.py:165,271` (kısmi şarj süresi mekanizması)

## Related

- [[partial_recharging]]
- [[sorun_ev_enerji_tuketim_modeli_basitlestirilmis]]
- [[karar_partial_charging_denklemleri_entegrasyonu_plani]]
- [[klon_dugum_node_replication]]
- [[sources/2026-08-09-ev_v1_1]]
