---
title: Sorun — Şarj/Yakıt İstasyonları ve Mola-İstasyon Bağıntıları Kodda Yok
tags: [sorun, ev, cv, istasyon, matematiksel-model-eksikliği]
source: raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx
date: 2026-08-09
status: güncel
---

# Sorun — Şarj/Yakıt İstasyonları ve Mola-İstasyon Bağıntıları Kodda Yok

## Sorun

Matematiksel modelde şarj/yakıt istasyonları kümesi (F) ve bu istasyonlardaki şarj süresini belirleyen karar değişkeni açıkça kurgulanmış. Buna ek olarak:
- Kısıt (11): mola bitiş zamanı ile sonraki noktaya varış zamanını düzenler.
- Kısıt (10): istasyonda mola verilmesi durumunda şarj/yakıt işleminin mola başlangıcından önce bitmesini gerektirir.

Kod tarafında ise ne bağımsız bir istasyon noktası kümesi ne de rota ortasında bir istasyona uğrayarak yakıt/şarj alma mantığı var. İstasyon yapısı hiç olmadığı için Kısıt (10) koda hiç yansımamış.

## Kapsam notu (Stage 2 kod doğrulamasıyla netleştirildi, 2026-08-09)

Bu eksiklik **CV kodu için tam doğrulandı**: `CV_model_gurobi_exact.py`'de istasyon kümesi (F) veya rota-ortası yakıt alma mantığı gerçekten yok. Üstelik `Fc` ve `alpha[Fc,Vc]` parametreleri fonksiyona geçiriliyor ama hiçbir kısıtta kullanılmıyor (bkz. [[sorun_cv_kullanilmayan_istasyon_parametreleri]]) — istasyon yapısının planlanıp yarım bırakıldığına dair somut kanıt.

**EV kodunda durum kısmen farklı** ve docx'ün genel iddiasından daha iyi durumda: `S`/`S_set` (istasyon kümesi) tanımlı ve aktif olarak kullanılıyor; `c22_station_recharge_lb` (`EV_v.1.1.py:334`) ve `c22_station_recharge_bigM` (340-353) ile istasyonlarda dolum kısıtları var. Eksik olan, "makale adımlar ve düzenlemeler.docx"'te belirtilen **klon düğüm** (aynı istasyona rota içinde birden fazla kez uğrama) — bu hâlâ kodda yok (bkz. [[klon_dugum_node_replication]]).

## Uygulama (Faz 2, 2026-08-11)

**EV tarafı: istasyon şarjı artık gerçekten çalışıyor.** Stage 2'de aktif olduğu doğrulanan `S`/`S_set` istasyon kısıtları, aslında `c20`'nin `c21`'i her zaman ezmesi yüzünden şarjı akışa hiç yansıtmıyordu (A1 sorunu — bkz. [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]). `src/EV_v_1_1_fixed.py:482-483`'teki `if i in S_set: continue` düzeltmesiyle bu artık gerçek bir dolum üretiyor (R5'te öncesi 0 çözüm/TIME_LIMIT, sonrası 8 çözüm, istasyon SoC örneği 751.54→1000.00). Klon düğüm eksikliği (bkz. [[klon_dugum_node_replication]]) hâlâ giderilmedi — Faz 2 kapsamı dışında kaldı.

**CV tarafı: değişmedi.** `src/CV_model_gurobi_fixed.py`'de de istasyon kümesi/rota-ortası yakıt alma mantığı yok — Faz 2, CV'nin istasyon eksikliğini gidermedi (Faz 2'nin CV'ye kattığı şeyler A6 non-overlap portlaması ve A7 yakıt tüketim oranı düzeltmesiydi, istasyon yapısı değil). `Fc`/`alpha` hâlâ kullanılmıyor — bkz. [[sorun_cv_kullanilmayan_istasyon_parametreleri]].

## Güncelleme (2026-08-22)

**CV tarafı:** hâlâ değişmedi — `raw/xml_data_loader.py` hâlâ `Fc=[0]` döndürüyor, gerçek istasyon listesi yok. `Fc`/`g_c`/`lc0` artık CV kodunda referans ediliyor ama pratik etkisi sıfır (bkz. [[sorun_cv_kullanilmayan_istasyon_parametreleri]] güncellemesi).

**EV tarafı — durum belirsizleşti:** `S`/`S_set` (gerçek istasyon listesi, `Kalabak_Info4ChargingStations.xml`'den) hâlâ aktif ve kullanılıyor. Ama EV18/EV19'un (eski c20/c21'in karşılığı) istasyon düğümlerinde bir atlama/istisna içermediği gözlemlendi — bu, Faz 2'nin A1 düzeltmesinin (istasyonlarda şarjın gerçekten akışa yansıması için gerekli olan atlama) yeni `raw/EV_v.1.1.py`'ye hiç taşınmadığı anlamına gelebilir. Doğrulanmadı, bkz. [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]] (`status: taslak`, kasıtlı olarak dokunulmadı). Eğer bu okuma doğruysa, "EV'de istasyon şarjı çalışıyor" iddiası yeniden sorgulanabilir hâle geliyor.

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- `raw/CV_model_gurobi_exact.py:13-27` (kullanılmayan Fc/alpha, eski 2026-08-09 hâli)
- `raw/EV_v.1.1.py:329-353` (aktif istasyon kısıtları)
- `src/EV_v_1_1_fixed.py:472-531` (A1 düzeltmesi)
- `src/CV_model_gurobi_fixed.py` (istasyon yapısı hâlâ yok)

## Related

- [[klon_dugum_node_replication]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
- [[sorun_cv_kullanilmayan_istasyon_parametreleri]]
- [[karar_klon_dugum_sarj_istasyonu_plani]]
- [[sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar]]
- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
