---
title: Karar — EV Modeline Depoda Tam Şarj / Dönüş Enerjisi / Müşteride Şarj Yok Kısıtları Eklendi (EV-24…EV-27)
tags: [karar, ev, enerji-kisiti, partial-recharging, cv-ev-simetrisi, v1.1]
source: raw/EV_v.1.1.py
date: 2026-08-22
status: güncel
---

# Karar — Yeni EV-24…EV-27 Kısıtları

## Bağlam

EV-17/EV-18/EV-19'un depo yaylarını kapsaması modeli infeasible yapıyordu
([[sorun_ev_depo_yaylarinda_dongusel_infeasibility]]). Bu yayları kısıttan çıkarmak
tek başına yeterli değildi: depo bacakları hiç kısıtlanmayınca enerji zinciri
**ankrajsız** kalıyor, `ye_j` yalnızca `[0, Q]` kutu sınırına takılıyor ve enerji
kısıtları fiilen devre dışı kalıyordu. CV modeli aynı sorunu yıllardır CV-22/23/24/25
ile çözüyordu; EV'de bu dört kısıtın karşılığı **hiç yoktu** (matematiksel model
dokümanında da yok — bkz. ilgili sayfadaki ÇELİŞKİ başlığı).

## Karar

CV'deki dört kısıtın birebir EV karşılıkları eklendi (`raw/EV_v.1.1.py:401-454`):

| Yeni | CV muadili | Anlam | Kod |
|---|---|---|---|
| **EV-24** | CV-23 | Depodan çıkışta üst sınır: `ye_j ≤ Q_k − h_e·d(0,j)·x_0jk + Q_k(1−x_0jk)` | `EV24_depo_sarj_ub_*` |
| **EV-25** | CV-24 | Depodan çıkışta alt sınır: `ye_j ≥ Q_k − h_e·d(0,j) − Q_k(1−x_0jk)` | `EV25_depo_sarj_lb_*` |
| **EV-26** | CV-25 | Dönüş bacağı enerjisi: `YE_i ≥ h_e·d(i,0)·x_i0k` | `EV26_donus_enerjisi_*` |
| **EV-27** | CV-22 | Müşteride şarj yok: `YE_i = ye_i, ∀i ∈ C` | `EV27_musteride_sarj_yok_*` |

EV-24 + EV-25 birlikte, `x_0jk = 1` iken `ye_j = Q_k − h_e·d(0,j)` eşitliğini verir —
yani **depo, çoklu seferin (EV-4) kullandığı tek "tam şarj" mekanizmasıdır**; CV'de de
durum aynıdır (`raw/CV_model_gurobi_exact.py:366-384`).

EV-26'da CV-25'in aksine `ye_i` yerine **`YE_i` (ayrılış enerjisi)** kullanıldı, çünkü
EV'de dönüş bacağı bir istasyondan da başlayabilir; müşteri düğümlerinde EV-27 gereği
`YE_i = ye_i` olduğundan davranış CV-25 ile birebir aynı kalır.

EV-27 olmadan model, fiziksel olarak imkânsız biçimde **bir müşteri düğümünde de şarj
olabiliyordu** (EV-20 yalnızca `ye_i ≤ YE_i ≤ Q_k` diyor). Keskin & Çatay (2016)
formülasyonunda da `Y_i = y_i` yalnızca istasyon olmayan düğümler için serbest
bırakılır. Ayrıca EV-27 olmadan A1 düzeltmesinin etkisi ölçülemez hâle gelirdi
(şarj her düğümde "bedava" olduğu için istasyona hiç gerek kalmazdı).

## Gurobi doğrulaması

C5 örneği, batarya `Q = 600 Wh`'a düşürülerek istasyon ziyareti zorunlu hâle getirildi
(normal `Q = 50000 Wh`, `h_e = 0.1553 Wh/m` ile menzil 322 km olduğundan bu veri
setinde istasyon hiç gerekmiyor):

- Rota sabitlenmiş keskin test (`0→1→5→8→4→0`): **FEASIBLE**;
  istasyon 8'de `ye = 0.0 → YE = 337.2 Wh`, müşteri 4'e varış `ye = 328.6 Wh`
  (= `h_e · d(4,0)` = dönüş için gereken minimum, yani EV-26 tam sıkı).
- Serbest arama: optimal-bulunan rota istasyondan geçiyor
  (`0→1→5→8(istasyon)→4→0`, `obj = 8371.2`).
- Normal `Q = 50000` ile C5: `obj = 8291.2` (CV C5 optimali ile aynı), istasyon
  kullanılmıyor — beklenen davranış.

## Bilinen sınırlama (düzeltilmedi, bilinçli)

`ye_i` / `YE_i` yalnızca **düğüm** indislidir (matematiksel model de böyle tanımlıyor:
docx "YE_i : i düğümünden ayrılış batarya seviyesi"). Bir şarj istasyonu birden fazla
kaynak (`k`) veya birden fazla sefer tarafından ziyaret edilirse hepsi **aynı**
`ye_s`/`YE_s` değişkenini paylaşır; bu, enerji muhasebesini yanlışlar. Faz 2'nin
`src/EV_v_1_1_fixed.py` dalı bunu `(düğüm, k)` indisine geçerek çözmüştü
([[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]). v1.1'de bu **model
seviyesinde** bir değişiklik olacağı için burada uygulanmadı; ayrıca ziyaret edilmeyen
düğümlerin `ye/YE` değerleri serbest kaldığından raporlamada anlamsız değerler
görünebilir (örn. hiç ziyaret edilmeyen istasyon 6 için `YE = 600.0`).

## Sources

- `raw/EV_v.1.1.py:401-454` (EV-24/25/26/27)
- `raw/CV_model_gurobi_exact.py:356-396` (CV-22/23/24/25 — desen kaynağı)
- `yeni dosyalarım/Matematiksel_Model_rev_v1.1/Matematiksel Model - CV ve EV.docx` (CV-22…CV-25; EV bölümünde karşılığı yok)

## Related

- [[sorun_ev_depo_yaylarinda_dongusel_infeasibility]]
- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
- [[karar_partial_charging_denklemleri_entegrasyonu_plani]]
- [[degisken_yakit_enerji_izleme]]
