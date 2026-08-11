---
title: CatBoost
tags: [entity, makine-öğrenmesi, tahminleme, kütüphane]
source: raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: taslak
---

# CatBoost

Gradient boosting tabanlı bir makine öğrenmesi kütüphanesi. TRSP projesinde henüz koda entegre edilmemiş, planlama aşamasında iki farklı rolde öneriliyor:

1. **Haftalık talep tahmini:** Geçmiş arıza kayıtları, hava durumu, bölge bazlı fiber altyapı yoğunluğu gibi verilerle gelecek haftanın iş yükünü (kaç teknisyene ihtiyaç duyulacağını) tahmin eder.
2. **İptal olasılığı tahmini (Cancellation Probability Forecasting):** Her iş emri için 0-1 arası bir iptal skoru üretir; bu skor Gurobi modeline veri beslenmeden önce bir ön işleme filtresi olarak kullanılır (bkz. [[karar_iptal_olasiligi_on_filtreleme_plani]]).

Ayrıca "makale adımlar ve düzenlemeler" belgesinde hibrit algoritmanın "Adım 1: Veri Ön İşleme ve Kümeleme" katmanında TOPSIS ile birlikte kullanılması öneriliyor — düğümleri aciliyet ve teknisyen yetkinliğine göre alt kümelere ayırmak için.

## Sources

- `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`

## Related

- [[topsis]]
- [[iptal_olasiligi_tahmini]]
- [[karar_iptal_olasiligi_on_filtreleme_plani]]
- [[karar_hibrit_algoritma_mimari_sirasi]]
- [[sources/2026-08-09-dinamik_tahminleme_adimlari_ve_veri]]
- [[sources/2026-08-09-makale_adimlar_ve_duzenlemeler]]
