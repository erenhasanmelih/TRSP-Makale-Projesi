---
title: İptal Olasılığı Tahmini (Cancellation Probability Forecasting)
tags: [kavram, makine-öğrenmesi, ön-filtreleme, operasyonel-verimlilik]
source: raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx
date: 2026-08-09
status: güncel
---

# İptal Olasılığı Tahmini (Cancellation Probability Forecasting)

Sahadaki en büyük zaman/kapasite kayıplarından birinin, teknisyenin adrese gitmesine rağmen müşterinin talebi iptal etmesi veya adreste bulunmaması olduğu tespitine dayanan bir ön-filtreleme mekanizması. [[catboost]] gibi bir makine öğrenmesi modeliyle her iş emri için 0-1 arasında bir iptal olasılık skoru hesaplanır.

## Mekanizma

1. **Ön İşleme Filtresi:** Gurobi modeline veri beslenmeden önce, geçmiş verilere dayanarak eğitilmiş ML modeli her iş emri için skor üretir.
2. **Önceliklendirme:** Skoru belirli bir eşiğin (örn. %80) üzerinde olan iş emirleri optimizasyona hiç sokulmadan filtrelenir. Daha düşük riskli ama şüpheli olanlar [[topsis]] ile ağırlıklandırılıp "düşük öncelikli" olarak rotanın sonuna eklenir.

## Beklenen fayda

İptal riski yüksek görevlere kaynak ayrılmasını önleyerek, araçların gereksiz karbon emisyonu yapmasını ve kapasite israfını engellemek; Gurobi'nin arama uzayını (search space) gereksiz iş emirlerinden arındırarak çözüm süresini hızlandırmak.

## Sources

- `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx`

## Related

- [[catboost]]
- [[topsis]]
- [[karar_iptal_olasiligi_on_filtreleme_plani]]
- [[rolling_horizon]]
