---
title: Karar (Faz 2) — src/ Klasörü ve raw/ İzolasyonu
tags: [karar, faz2, mimari, raw-izolasyonu, kod]
source: src/EV_v_1_1_fixed.py; src/CV_model_gurobi_fixed.py; src/xml_data_loader_fixed.py
date: 2026-08-11
status: güncel
---

# Karar (Faz 2) — src/ Klasörü ve raw/ İzolasyonu

## Karar

Faz 1'de tespit edilen 7 kritik sorun (A1, A7, A6, A4, A2+C1, A5, C2), `raw/` klasörü **hiç değiştirilmeden** (CLAUDE.md Hard Rule 1), kök dizinde yeni açılan `src/` klasörü altına konan üç YENİ dosyada düzeltildi:

| Orijinal (`raw/`, salt-okunur) | Düzeltilmiş kopya (`src/`) |
|---|---|
| `raw/EV_v.1.1.py` | `src/EV_v_1_1_fixed.py` |
| `raw/CV_model_gurobi_exact.py` | `src/CV_model_gurobi_fixed.py` |
| `raw/xml_data_loader.py` | `src/xml_data_loader_fixed.py` |

## Gerekçe

`raw/`'a yazma, taşıma, yeniden adlandırma veya silme wiki şemasının en katı kuralı (CLAUDE.md §7.1). Bu yüzden düzeltmeler orijinal dosyaların üzerine yazılmadı; her dosyanın "fixed" son ekli bir kopyası açıldı ve tüm değişiklikler bu kopyalarda yapıldı. `src/EV_v_1_1_fixed.py`'nin başında bunu açıkça belirten bir yorum satırı var: *"Kaynak: raw/EV_v.1.1.py - Faz 2 duzeltmeleri (A1, A7, A6, A4, A2+C1, A5, C2) uygulanmistir."* (`src/EV_v_1_1_fixed.py:16`).

## Neden xml_data_loader.py da kopyalandı

A7'nin (CV'de `h_c=1.0` sabit, `EnergyConsumptionRate` XML'den okunmuyor) kök nedeni `xml_data_loader.py`'deki veri hazırlama fonksiyonlarındaydı (`prepare_ev_data_from_instance`/CV karşılığı), `CV_model_gurobi_exact.py`'nin kendisinde değil. Eren'e üç seçenek sunuldu (Faz 1 analiz aşamasında): (a) `h_c`'yi `build_model()` çağrısında elle geçirmek, (b) `CV_model_gurobi_fixed.py`'nin içine XML okuma mantığını gömmek, (c) `xml_data_loader.py`'yi de `src/`'e kopyalayıp orada düzeltmek. Eren (c)'yi onayladı — bu, veri yükleme mantığının tek bir kaynaktan (`xml_data_loader_fixed.py`) hem CV hem EV modeli için tutarlı kalmasını sağlıyor.

## Doğrulama

R5 problem setinde Gurobi 13 ile üç dosya birlikte çalıştırıldı: EV `status=OPTIMAL, obj=10116.10`; CV `status=OPTIMAL, obj=10116.10` — iki modelin aynı problem setinde aynı objektif değere ulaşması, `src/` kopyalarının birbirleriyle ve ortak veri yükleyiciyle tutarlı çalıştığının çapraz doğrulamasıdır.

## Kapsam notu

`resolve_data_root()` fonksiyonu her iki model dosyasına da eklendi çünkü orijinal `os.path.dirname(__file__)` tabanlı veri/çıktı yolu deseni, dosyalar `src/`'e taşınınca kırılırdı — veri hâlâ `raw/`'dan okunmalı, çıktı ise `src/sonuclar/`'a yazılmalı. Detay: `entities/model_calistirma_parametreleri_ev.md`.

## Sources

- `src/EV_v_1_1_fixed.py:1-26`
- `src/CV_model_gurobi_fixed.py`
- `src/xml_data_loader_fixed.py`
- `raw/EV_v.1.1.py`
- `raw/CV_model_gurobi_exact.py`
- `raw/xml_data_loader.py`

## Related

- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
- [[karar_a6_cv_non_overlap_portlamasi]]
- [[karar_a4_zaman_penceresi_bigm_kosullandirma]]
- [[karar_c2_tight_big_m_uygulamasi]]
- [[model_calistirma_parametreleri_ev]]
- [[gurobi_mip_cozucusu]]
