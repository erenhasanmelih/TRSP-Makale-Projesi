---
title: Rolling Horizon (Yuvarlanan Ufuk)
tags: [kavram, çizelgeleme, geri-bildirim-döngüsü, sistem-mimarisi]
source: raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx
date: 2026-08-09
status: güncel
---

# Rolling Horizon (Yuvarlanan Ufuk)

Haftalık (taktiksel) ve günlük (operasyonel) planlama seviyelerinin kopuk çalışmasını önlemek için kullanılan bir sistem entegrasyon mantığı. Haftalık plan 7 günlük bir teorik çerçeve çizer; her günün sonunda gerçekleşen operasyonel veriler (gecikmeler, yarına sarkan işler, arızalanan araçlar) bir **geri bildirim döngüsü (feedback loop)** olarak sisteme aktarılır ve ertesi günün + kalan haftanın planını revize eder.

## TRSP projesindeki 3 aşamalı mimarideki yeri

1. Haftalık Çizelgeleme (Taktiksel/Makro)
2. Günlük Atama ve Rotalama (Operasyonel/Mikro)
3. **Sistem Entegrasyonu (Rolling Horizon)** — 1 ve 2'yi birbirine bağlayan geri bildirim katmanı

Detay: bkz. [[karar_3_asamali_rolling_horizon_sistem_mimarisi]].

## Sources

- `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx`

## Related

- [[karar_3_asamali_rolling_horizon_sistem_mimarisi]]
- [[karar_gunluk_haftalik_planlama_pool_plani]]
- [[iptal_olasiligi_tahmini]]
- [[sources/2026-08-09-dinamik_tahminleme_adimlari_ve_veri]]
