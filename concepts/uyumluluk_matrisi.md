---
title: Uyumluluk Matrisi (Compatibility Matrix)
tags: [kavram, teknisyen-araç-eşleşmesi, kısıt, renk-modeli]
source: raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Uyumluluk Matrisi (Compatibility Matrix)

İki teknisyenin bir araya gelerek bir ekip oluşturması ve bu ekibin sadece kendi yetkinliğindeki işlere (ör. P1-5G Montaj) gidebilmesini kısıtlayan matris/parametre. [[colored_tsp]] literatüründeki "Renkler (Colors)" ve "Uyumluluk Matrisi (Compatibility Constraints)" kavramlarına dayanıyor.

## Matematiksel modelde planlanan tanım

Deterministik bir parametre (renk/yetkinlik matrisi) olarak Gurobi kısıtlarına açıkça yedirilmesi planlanıyor.

## Kodda mevcut durum

Kodda `Ti[j]` ile Python seviyesinde filtreleme yapılıyor — yani uyumluluk mantığı Gurobi kısıtı olarak değil, veri hazırlama aşamasında (hangi ekiplerin hangi müşteriye "izinli" olduğunu belirleyen bir liste olarak) uygulanıyor. Bu, "makale adımlar ve düzenlemeler" belgesinde CV modelinin bir eksikliği olarak işaretleniyor.

## Güncelleme (Faz 2, 2026-08-11)

Uyumluluk mantığı hâlâ Gurobi kısıtı olarak değil, veri/model kurma aşamasında uygulanıyor — ama uygulama noktası değişti. Faz 2'de `_crew_allowed(node, t)` adlı bir yardımcı fonksiyon (A5), 3B `x[i,j,k]` indirgemesiyle (C1) aynı refaktörde eklendi: uyumsuz (düğüm, ekip) çiftleri için `x` değişkeni **hiç üretilmiyor** (`arc_ks` listesi kurulurken filtreleniyor, bkz. `src/EV_v_1_1_fixed.py:134-145`, `src/CV_model_gurobi_fixed.py:53-64`). Doğrulama: uyumsuz kombinasyonlar için üretilen `x` sayısı 0. Bu hâlâ "Gurobi kısıtı" değil "üretim-öncesi filtre" ama artık Python seviyesinde ayrık bir liste kontrolü değil, karar değişkeni kurulumunun kendisine gömülü. Detay: [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]].

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`
- `src/EV_v_1_1_fixed.py:134-145`
- `src/CV_model_gurobi_fixed.py:53-64`

## Related

- [[karar_rc13_asgari_paket_uygulamasi]] (Ö1 UYGULANDI — `x`/`w` artık yetkinliksiz `(i,j,kk)` için `UB=0`)
- [[sorun_rc13_darbogaz_kok_neden_analizi]] (`x` üzerinde uygulanmamış yetkinlik filtresi, RC13'te `NumVars` %-70 kazanç kaynağı — Ö1)
- [[colored_tsp]]
- [[karar_uyumluluk_matrisi_cizelgeleme_plani]]
- [[model_karar_degiskenleri_ve_parametreleri]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
