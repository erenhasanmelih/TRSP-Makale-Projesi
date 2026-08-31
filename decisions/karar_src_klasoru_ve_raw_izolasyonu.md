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

`resolve_data_root()` fonksiyonu her iki model dosyasına da eklendi çünkü orijinal `os.path.dirname(__file__)` tabanlı veri/çıktı yolu deseni, dosyalar `src/`'e taşınınca kırılırdı — veri hâlâ `raw/`'dan okunmalı, çıktı ise `src/sonuclar/`'a yazılmalı. Detay: bu bilgiyi belgeleyen sayfa (`entities/model_calistirma_parametreleri_ev.md`) 2026-08-22'de silindi; ENABLE_PAIR_CREWS vb. bayraklar zaten v1.1'de kaldırıldı.

## GÜNCELLEME (2026-08-22) — raw/ Tabanı Değişti, src/*_fixed.py Artık Eski Bir Taban Üzerine Kurulu

**Durum değişikliği:** Eren'in açık onayıyla (CLAUDE.md Hard Rule §7.1'in bilinçli, bu seferlik istisnası — kullanıcı talebi, ajan tarafından tek taraflı alınmış bir karar değil), `raw/CV_model_gurobi_exact.py`, `raw/EV_v.1.1.py` ve `raw/xml_data_loader.py` **2026-08-22 tarihinde tamamen yeni bir "v1.1" içerikle DEĞİŞTİRİLDİ** (+ yeni `raw/solution_validator.py` eklendi). Bu, yukarıdaki tablonun temel varsayımını geçersiz kılıyor: **"Orijinal (`raw/`, salt-okunur)" sütunundaki dosyalar artık bu sayfanın (2026-08-11 tarihli) yazıldığı andaki içerikle AYNI DEĞİL.**

**Somut etki — `src/*_fixed.py` dosyaları artık şu ana raw/ tabanıyla senkron değil:**

1. **`src/EV_v_1_1_fixed.py`**, eski `raw/EV_v.1.1.py`'nin (route_start/route_end/ord_* teknisyen-çakışma-önleme bloğu, `y_route`, `ENABLE_PAIR_CREWS`/`FEASIBILITY_FOCUSED_PARAMS` bayrakları, Tee/docx otomatik raporlama, 12 Gurobi tuning parametresi + IIS diagnostiği olan sürüm) türetilmiş bir kopyasıdır. **Yeni `raw/EV_v.1.1.py` bu mekanizmaların HİÇBİRİNİ içermiyor** — tamamen farklı, çok daha sade bir yapıya (basit `z_veh`/EV-22/EV-23 tekillik kısıtları, çoklu sefer EV-4, tek bir `data` dict parametresi hâlâ korunmuş ama içeriği baştan yazılmış) sahip. Yani `src/EV_v_1_1_fixed.py` artık "güncel `raw/EV_v.1.1.py`'nin düzeltilmiş hâli" değil, **"artık var olmayan bir önceki `raw/EV_v.1.1.py` sürümünün düzeltilmiş hâli"**dir.
2. **`src/CV_model_gurobi_fixed.py`** de benzer şekilde eski `raw/CV_model_gurobi_exact.py`'den türetildi (`c4_{v}` tek-sefer, sabit `100000.0` Big-M, `Fc`/`alpha`/`g_c`/`k`/`lc0` tamamen ölü). **Yeni `raw/CV_model_gurobi_exact.py`** artık kendi başına çoklu sefer (`CV4_multitrip`, ≤3), kendi tight-Big-M ifadeleri (sabit `100000.0` YOK) ve kendi araç-ekip/teknisyen tekillik kısıtlarını (`CV27`/`CV28`, `z` değişkeni) içeriyor — **A2+C1 (index reduction), C2 (tight-M) ve A6 (teknisyen çakışma) sorun kodlarının kapsadığı sorunların çoğu, `src/`'deki düzeltmelerden BAĞIMSIZ, farklı bir mekanizmayla `raw/`'un kendisinde de fiilen ele alınmış** (bkz. [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]] ve [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]).
3. **A1 (EV şarj c20/c21 çakışması) ve A7 (CV `h_c` sabiti) için durum TERSİNE** işliyor: yeni `raw/EV_v.1.1.py` ve `raw/xml_data_loader.py`, Faz 2'nin bu iki düzeltmesini **miras almamış** — aynı mimari kusur (istasyon çıkışında şarj-öncesi zincirin şarj-sonrası zinciri ezmesi; `h_c=1.0` sabiti, `EnergyConsumptionRate` XML'den okunmuyor) yeni kodda da statik okumayla tespit edildi. Ayrıntı ve doğrulanmamışlık uyarısı: [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]].

**Ne yapılmadı / ne bekliyor:** `src/*_fixed.py` dosyaları bu ingest kapsamında **GÜNCELLENMEDİ** — bu, matematiksel/algoritmik bir karar (hangi düzeltmelerin yeni `raw/` tabanına yeniden uygulanacağı) gerektiriyor ve kütüphanecinin (bu ajanın) yetki alanı dışında. `trsp-exact-model-mimari`'nin şu soruyu değerlendirmesi gerekiyor: Faz 2'nin C1/C2/A2/A5/A6 kazanımları yeni `raw/` tabanında zaten (farklı bir mekanizmayla) mevcut olduğuna göre, `src/*_fixed.py`'yi yeni tabana göre yeniden mi türetmeli, yoksa yeni `raw/` kodunu doğrudan makale/deney tabanı olarak mı kabul etmeli (ki bu durumda `src/` klasörünün amacı kökten değişir)?

**Bu sayfanın geri kalanı (aşağıdaki orijinal içerik) 2026-08-11 tarihli, o zamanki `raw/` durumuna göre hâlâ doğru bir tarihsel kayıttır — silinmedi, sadece artık "güncel raw/" ile eşleşmiyor.**

## Sources

- `src/EV_v_1_1_fixed.py:1-26`
- `src/CV_model_gurobi_fixed.py`
- `src/xml_data_loader_fixed.py`
- `raw/EV_v.1.1.py` (2026-08-22 sonrası hâli — Faz 2 öncesi/sonrası hiçbir düzeltmeyi yansıtmıyor)
- `raw/CV_model_gurobi_exact.py` (2026-08-22 sonrası hâli)
- `raw/xml_data_loader.py` (2026-08-22 sonrası hâli)
- `git show HEAD:raw/EV_v.1.1.py`, `git show HEAD:raw/CV_model_gurobi_exact.py`, `git show HEAD:raw/xml_data_loader.py` — `src/*_fixed.py`'nin türetildiği ESKİ raw/ içeriğine erişim (git geçmişi)

## Related

- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
- [[karar_a6_cv_non_overlap_portlamasi]]
- [[karar_a4_zaman_penceresi_bigm_kosullandirma]]
- [[karar_c2_tight_big_m_uygulamasi]]
- [[gurobi_mip_cozucusu]]
- [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]]
- [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]
- [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]]
- [[sources/2026-08-22-ev_v1_1_rewrite]]
