---
title: Klon Düğüm / Node Replication (Şarj İstasyonu Çoğullama)
tags: [kavram, ev, matematiksel-model, şarj-istasyonu]
source: raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Klon Düğüm / Node Replication (Şarj İstasyonu Çoğullama)

EV'lerin bir rotanın ortasında aynı şarj istasyonuna birden fazla kez uğrayabilmesini modelleyebilmek için, her fiziksel istasyon düğümünün matematiksel modelde birden fazla "klonlanmış" (dummy) düğüm olarak temsil edilmesi tekniği. Her klon için ayrı giriş-çıkış akış kısıtları tanımlanır.

## TRSP projesindeki durum

`makale adımlar ve düzenlemeler.docx` belgesinde, mevcut EV modelinin bu yapıyı içermediği ve bunun EV modelini makale standardına göre eksik kıldığı belirtiliyor. [[partial_recharging]] ile doğrudan ilişkili: kısmi şarjın anlamlı olabilmesi için aracın aynı istasyona tekrar uğrayabilmesi gerekir.

## Sources

- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[partial_recharging]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
- [[karar_klon_dugum_sarj_istasyonu_plani]]
