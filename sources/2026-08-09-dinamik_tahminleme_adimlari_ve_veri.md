---
title: Dinamik Tahminleme Adımları ve Veri
tags: [yönerge, rolling-horizon, catboost, sentetik-veri, çizelgeleme]
source: raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx
date: 2026-08-09
status: güncel
---

# Dinamik Tahminleme Adımları ve Veri

## Amaç

TRSP için 3 aşamalı bir planlama mimarisi (haftalık taktiksel → günlük operasyonel → rolling horizon geri bildirimi) tanımlamak ve bu mimariye makine öğrenmesi destekli tahminleme (talep, iptal olasılığı) ile sentetik veri üretimini entegre etmek.

## Ne yapıldı

Belge, TRSP'nin sadece bir günlük rotalama problemi değil, çok seviyeli bir planlama sistemi olarak kurgulanmasını öneriyor:

- **1. Aşama — Haftalık Çizelgeleme (Taktiksel/Makro):** Geçmiş arıza kayıtları, hava durumu, bölge bazlı fiber altyapı yoğunluğu gibi verilerle **CatBoost** kullanılarak talep tahmini yapılır. Vardiya/kapasite planlaması ve **TOPSIS** ile teknisyen performans/uzmanlık sıralaması bu aşamada yapılır.
- **2. Aşama — Günlük Atama ve Rotalama (Operasyonel/Mikro):** Window-Wise Sweep gibi hızlı sezgisellerle warm-start rotaları üretilir; Python + Gurobi entegrasyonu ile kesin görev ataması yapılır (EV/CV kısıtları, mola, zaman pencereleri); gün içi iptal/uzama gibi olaylar için dinamik revizyon uygulanır.
- **3. Aşama — Sistem Entegrasyonu (Rolling Horizon):** Haftalık plan 7 günlük teorik çerçeve çizer; her günün sonunda gerçekleşen operasyonel veriler (gecikme, ertelenen iş, arızalanan araç) bir geri bildirim döngüsü olarak ertesi günün ve kalan haftanın planını revize eder.

**Ek detaylar** olarak iki yeni modül öneriliyor:

1. **İptal İhtimali Hesaplama (Cancellation Probability Forecasting):** CatBoost ile her iş emri için 0-1 arası iptal olasılık skoru; Gurobi'ye veri beslenmeden önce bir ön işleme (pre-processing) filtresi olarak çalışır. Skoru %80 üzerinde olan iş emirleri optimizasyona hiç sokulmaz; düşük riskli ama şüpheli olanlar TOPSIS ile ağırlıklandırılıp rotanın sonuna eklenir.
2. **Veri Türetme (Data Augmentation & Generation):** Solomon standartlarına göre (R/C/RC) sentetik müşteri lokasyonu üreten bir Python betiği; 5 görev tipi (P1: 5G Montaj, P2: Fiber vb.), 60-120 dakika hizmet süreleri ve SLA'ya uygun zaman pencereleri sentetik müşterilere rastgele atanır.

## Anahtar noktalar

- Sistem üç seviyeli: taktiksel (haftalık) → operasyonel (günlük) → geri bildirim (rolling horizon).
- CatBoost iki farklı yerde kullanılıyor: (a) haftalık talep tahmini, (b) iş emri iptal olasılığı tahmini.
- TOPSIS iki farklı yerde kullanılıyor: (a) teknisyen performans sıralaması, (b) düşük riskli ama şüpheli iş emirlerinin önceliklendirilmesi.
- Warm-start için Window-Wise Sweep önerisi, [[warm_start]] kavramıyla örtüşüyor.

## Kararlar

- [[karar_3_asamali_rolling_horizon_sistem_mimarisi]]
- [[karar_iptal_olasiligi_on_filtreleme_plani]]
- [[karar_sentetik_veri_uretici_solomon_plani]]

## Açık konular

- İptal olasılığı eşiği (%80) hangi veri setiyle kalibre edilecek — belgede belirtilmemiş.
- Rolling horizon geri bildirim döngüsünün optimizasyon modeliyle teknik entegrasyonu (kod seviyesinde) henüz tanımlanmamış.

## Sources

- `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx` (tam metin)

## Related

- [[catboost]]
- [[topsis]]
- [[warm_start]]
- [[rolling_horizon]]
- [[iptal_olasiligi_tahmini]]
