---
title: CV_model_gurobi_exact.py — CV Exact MIP Modeli
tags: [kaynak, kod, cv, gurobi, mip]
source: raw/CV_model_gurobi_exact.py
date: 2026-08-09
status: güncel
---

# CV_model_gurobi_exact.py — CV Exact MIP Modeli

## Amaç

Konvansiyonel araç (CV) filosu için teknisyen rotalama/çizelgeleme problemini Gurobi ile tam (exact) MIP modeli olarak kuran ve çözen script. `xml_data_loader` modülünden gelen problem/araç/çalışan verilerini kullanır.

## Ne yapıldı

`build_model(...)` fonksiyonu (satır 13-197) modeli kuruyor:

- **Karar değişkenleri** (satır 21-27): `x[i,j,v,t]` (ikili, arc-araç-ekip ataması), `tau[i,t]` (varış zamanı), `L[i,t]` (kullanılmıyor gibi görünüyor — tanımlı ama constraint'lerde referans yok), `YC[i]`/`yc[i]` (depo çıkışı / güncel yakıt seviyesi), `w[i,j,t]` (mola indikatörü), `alpha[Fc,Vc]` (tanımlı ama **hiçbir kısıtta kullanılmıyor** — muhtemelen yarım kalmış istasyon/yakıt maliyeti modellemesi kalıntısı).
- **Amaç fonksiyonu** (satır 38-41): toplam mesafeyi minimize et.
- **Kısıtlar:** c2 (her müşteriye yetkinlikli ekip girişi, 44-48), c3 (arc en fazla 1 kez, 50-51), **c4 (satır 53-54: her aracın günde en fazla 1 kez depodan çıkışı — `<= 1`, TEK SEFER)**, c5 (her ekip günde en fazla 1 rota, 56-57), c6 (akış korunumu, 59-66), c8_zaman_ilerleme (zaman ilerlemesi, Big-M=`100000.0`, 74-86), mola_max1 (mola opsiyonel `<=1`, 88-96), mola_yoksa_erken_donus (98-107), mola_yol_ustu_onayi + mola_baslama sınırları (109-125), c16/c17 (zaman pencereleri, 128-139), c18 (ec≤tau≤lc, 141-144), c20/c21 (yakıt takibi `yc`/`YC`, 146-165), c22 (depoda dolum yok, `YC[i]==yc[i]`, 167-171), c_return_fuel / c_full_depot (173-195).
- `format_time()` (200-207): saniyeyi `+28800` kaydırmalı saat formatına çevirir (08:00 referans).
- `print_cv_solution()` (210-310): çözümü Türkçe, emoji'li konsol raporu olarak basar.
- `select_instances()` (313-332): kullanıcıdan hangi problem örneklerinin çalıştırılacağını interaktif sorar.
- `__main__` bloğu (335-456): `trsp_problem_sets/` altındaki XML örnekleri yükler, `Info4Employee.xml`'den teknisyen/yetkinlik haritasını okur, her örnek için `itertools.combinations(active_techs, 2)` ile ikili ekipler oluşturur (414-417), modeli kurar, `.lp` dosyasına yazar, `TimeLimit=900` (15 dk) ile çözer.

## Anahtar noktalar

- **Kritik doğrulama — [[ÇELİŞKİ]]:** "kodda ve matematiksel modeldeki farklılıklar.docx" belgesi kodda `c4_multitrip_{v}` isimli, aracın günde 3 defaya kadar tur atmasına izin veren bir kısıt olduğunu iddia ediyor. **Bu satırda (53-54) böyle bir kısıt yok** — mevcut kısıt `c4_{v}`, `<= 1` ile **tek sefer** sınırlaması yapıyor, yani matematiksel modelin Kısıt (3)'üyle **uyumlu**. Bkz. [[celiski_single_trip_vs_multitrip]] (güncellendi).
- `build_model()` imzası 20'ye yakın pozisyonel parametre alıyor (`N, N0, C, Vc, V, T, Ti, Fc, A, d, tt, st, G, ec, lc, es, ls, el, ll, h_c, g_c, k, lc0, node_labels`); bunlardan **`Fc`, `g_c`, `k`, `lc0`, `node_labels` fonksiyon gövdesinde hiç kullanılmıyor**. `Fc` sadece kullanılmayan `alpha` değişkenini boyutlandırmak için var — bu, CV modelinde bir istasyon/yakıt-maliyeti yapısının planlanıp yarım bırakıldığına dair somut kod kanıtı (bkz. [[sorun_sarj_yakit_istasyonlari_kodda_yok]]).
- `L[i,t]` karar değişkeni tanımlı ama hiçbir kısıtta geçmiyor — muhtemelen kullanılmayan/atıl bir değişken (yük (load) takibi için düşünülmüş olabilir, EV modelinde de aynı isimde `L` var ve o da kullanılmıyor).
- Mola/zaman kısıtları (c8, mola_max1, mola_yoksa_erken_donus, mola_baslama sınırları) `EV_v.1.1.py`'deki karşılıklarıyla satır satır neredeyse birebir aynı — iki dosya arasında kod paylaşımı/kopyalama olduğu açık.

## Kararlar

- [[celiski_single_trip_vs_multitrip]] (güncellendi — kod, docx iddiasını doğrulamadı)
- [[sorun_sarj_yakit_istasyonlari_kodda_yok]] (Fc/alpha kanıtıyla güncellendi)
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]] (satır 414-417 ile doğrulandı)
- [[sorun_hardcoded_mola_parametreleri]] (satır 70-72 ile doğrulandı)
- [[karar_molasiz_erken_donus_kurali_kod]] (satır 98-107 ile doğrulandı)
- [[karar_operasyonel_zaman_kaydirma_format_time]] (satır 200-207 ile doğrulandı)

## Açık konular

- `L[i,t]` ve `alpha[Fc,Vc]` değişkenlerinin ne amaçla eklendiği ama hiç kullanılmadığı netleşmemiş — bu ölü kod mu yoksa yarım kalmış bir özellik mi?
- `c4_multitrip_{v}` kısıtının hangi kod sürümünde var olduğu (docx'ün tarif ettiği versiyon) bilinmiyor — mevcut `raw/CV_model_gurobi_exact.py` (18 Mayıs 2025 tarihli) bunu içermiyor, docx ise 7 Ağustos 2026 tarihli (docx dosya, koddan sonra yazılmış). Ya docx yanlış hatırlıyor ya da kodun ara bir sürümünde bu kısıt vardı ve sonra kaldırıldı.

## Sources

- `raw/CV_model_gurobi_exact.py` (tam dosya, 456 satır)

## Related

- [[model_karar_degiskenleri_ve_parametreleri]]
- [[degisken_x_arc_tahsisi]]
- [[degisken_yakit_enerji_izleme]]
- [[parametre_big_m_100000]]
- [[parametre_mola_zaman_sabitleri]]
- [[build_model_fonksiyonu]]
- [[sources/2026-08-09-ev_v1_1]]
