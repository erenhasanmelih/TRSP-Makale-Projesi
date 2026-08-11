---
title: Kodda ve Matematiksel Modeldeki Farklılıklar
tags: [yönerge, çelişki, kod-model-uyumsuzluğu, kritik]
source: raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx
date: 2026-08-09
status: güncel
---

# Kodda ve Matematiksel Modeldeki Farklılıklar

## Amaç

Teorik matematiksel modelde kurgulanmış ama Gurobi kodunda uygulanmamış noktaları, ve tersine kodun modele ek olarak getirdiği operasyonel esneklikleri sistematik olarak tespit etmek. Bu belge, wiki içinde en kritik kaynaktır — çünkü doğrudan çelişki ve tutarsızlık tespiti içeriyor.

## Ne yapıldı

Belge iki başlık altında toplam 10 madde listeliyor.

**Matematiksel modelde olup kodda OLMAYAN noktalar:**
1. Şarj/Yakıt İstasyonları (F kümesi) ve ara nokta dolumu — modelde açıkça kurgulu, kodda istasyon noktası kümesi veya rota ortası yakıt alma mantığı yok.
2. Kısmi Şarj (Partial Recharge) ve şarj hızı dinamikleri — model Kısıt (17) ve (19) ile şarj hızı katsayısı, maksimum şarj süresi hesaplıyor; kodda böyle bir dolum süresi hesabı yok, sadece tüketim katsayısı × mesafe ile azaltma var.
3. Tam bir öğle molası zorunluluğu — model Kısıt (12) `=1` ile zorunlu kılıyor; kodun `mola_max1_{t}` kısıtı `<=1` ile opsiyonel yapıyor.
4. Araçların tekil çıkış (Single-Trip) sınırı — model Kısıt (3) her aracın günde en fazla 1 kez depodan çıkabilmesini güvence altına alıyor; kodda bu kural yok.
5. Mola ve istasyon varış bağıntıları — model Kısıt (11) mola bitiş/sonraki nokta varış zamanını, Kısıt (10) istasyonda şarj işleminin mola başlangıcından önce bitmesini düzenliyor; istasyon yapısı kodda olmadığı için Kısıt (10) koda hiç yansımamış.

**Kodda olup matematiksel modelde OLMAYAN noktalar:**
6. Çoklu Tur (Multi-Trip) izni — kodda `c4_multitrip_{v}` kısıtı, bir aracın günde 3 defaya kadar tur atmasına izin veriyor.
7. Dinamik Teknisyen Ekibi (Kombinasyon) Oluşturma — `itertools.combinations(active_techs, 2)` ile teknisyenler ikili eşleştirilip yetenekleri birleştirilerek yeni "ekip (crew)" listesi oluşturuluyor; modelde T kümesi sadece bireysel teknisyenleri temsil ediyor.
8. Sabit (Hardcoded) Mola Parametreleri — model mola zamanlarını esnek parametreler üzerinden alırken, kod `break_duration=3600`, `break_min=13800`, `break_max=15000` olarak sabitliyor.
9. Molasız Görevler İçin Erken Dönüş Kuralı — kodun `mola_yoksa_erken_donus_{i}_{v}_{t}` kısıtı, mola kullanılmadıysa depoya dönüşü Big-M ile daha erkene zorluyor; modelde mola zaten zorunlu olduğundan böyle bir alternatif kısıt yok.
10. Operasyonel Raporlama ve Zaman Kaydırma — `print_cv_solution` fonksiyonunda `shifted_seconds = seconds + 28800` ile saniyeleri 08:00 başlangıçlı saat formatına çeviren bir arayüz/çıktı adımı; teorik modelin ilgilenmediği bir konu.

## Anahtar noktalar

- Maddeler 3 ve 4, doğrudan model-kod **çelişkisi** (aynı kural iki farklı yerde birbirini tutmuyor); maddeler 1, 2, 5 modelde olup kodda **eksik**; maddeler 6, 7, 8, 9, 10 kodun modele göre getirdiği **ek** esneklik/detaylardır.
- Bu belge Full Path.docx'teki Adım 1-3 revizyon planının doğrudan gerekçesidir: index reduction, tight Big-M ve partial charging planları bu tespitlere dayanıyor.

## Kararlar

- [[celiski_single_trip_vs_multitrip]]
- [[celiski_ogle_molasi_zorunlulugu]]
- [[sorun_sarj_yakit_istasyonlari_kodda_yok]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]
- [[sorun_hardcoded_mola_parametreleri]]
- [[karar_molasiz_erken_donus_kurali_kod]]
- [[karar_operasyonel_zaman_kaydirma_format_time]]

## Açık konular

- Bu 10 maddenin hangilerinin makale yayınlanmadan önce mutlaka kapatılması (kod=model tutarlılığı) gerektiği, hangilerinin bilinçli tasarım tercihi olarak kalabileceği (ör. multi-trip esnekliği belki kalıcı bir iyileştirme olabilir) henüz karara bağlanmamış.
- Stage 2 (Python dosyaları) ingest edildiğinde bu 10 maddenin kod satır referanslarıyla doğrulanması gerekiyor.

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx` (tam metin)

## Related

- [[model_karar_degiskenleri_ve_parametreleri]]
- [[partial_recharging]]
- [[tight_big_m]]
