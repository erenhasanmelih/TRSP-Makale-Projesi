---
title: İndeks
tags: [index]
source: n/a
date: 2026-08-09
status: güncel
---

# İndeks

TRSP (Teknisyen Rotalama ve Çizelgeleme Problemi) bilgi arşivinin içerik kataloğu. Her ingest sonrası güncellenir. Sorgu öncesi ilk okunacak dosya budur.

## Kaynaklar (sources/)

| Sayfa | Özet | Kaynak dosya |
|---|---|---|
| [2026-08-09-dinamik_tahminleme_adimlari_ve_veri](sources/2026-08-09-dinamik_tahminleme_adimlari_ve_veri.md) | 3 aşamalı (haftalık/günlük/rolling horizon) planlama mimarisi, CatBoost/TOPSIS kullanım noktaları, iptal olasılığı ve sentetik veri üretimi | `raw/Yönergelerimiz/dinamik tahminleme adımları ve veri .docx` |
| [2026-08-09-ek_noktalar_ve_makaleleri](sources/2026-08-09-ek_noktalar_ve_makaleleri.md) | 4 alt problem (rotalama, iş çizelgeleme, teknisyen çizelgeleme, uyumluluk) için 7 literatür örneği ve yöntemleri | `raw/Yönergelerimiz/EK NOKTALAR VE MAKALELERİ.docx` |
| [2026-08-09-full_path](sources/2026-08-09-full_path.md) | Projenin üst düzey yol haritası: 4 adımlı model revizyonu + 3 fazlı uygulama planı | `raw/Yönergelerimiz/Full Path.docx` |
| [2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar](sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar.md) | Kritik: model↔kod arasındaki 10 farklılık (çelişki + eksik + ek esneklik) | `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx` |
| [2026-08-09-makale_adimlar_ve_duzenlemeler](sources/2026-08-09-makale_adimlar_ve_duzenlemeler.md) | Makale amacı, CV/EV model eksikleri, literatür atıf haritası, hibrit algoritma geliştirme sırası | `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx` |
| [2026-08-22-cv_model_gurobi_exact_v1_1](sources/2026-08-22-cv_model_gurobi_exact_v1_1.md) | **v1.1 yeniden yazım** — çoklu sefer (CV-4≤3), z/CV-27/28 tekillik, raw/'da da tight-M ve 3B x, kk_name | `raw/CV_model_gurobi_exact.py` |
| [2026-08-22-ev_v1_1_rewrite](sources/2026-08-22-ev_v1_1_rewrite.md) | **v1.1 yeniden yazım** — eski EV-özgü karmaşıklık (route_start/end, 12 param, docx raporlama) tamamen kaldırıldı, EV artık CV ile simetrik | `raw/EV_v.1.1.py` |
| [2026-08-22-xml_data_loader_v1_1](sources/2026-08-22-xml_data_loader_v1_1.md) | İlk source sayfası — ortak veri hazırlama katmanı, `h_c=1.0` sabiti (regresyon riski) | `raw/xml_data_loader.py` |
| [2026-08-22-solution_validator](sources/2026-08-22-solution_validator.md) | Yeni dosya — çözüm sonrası tutarlılık doğrulayıcısı (sefer sırası + araç çakışması) | `raw/solution_validator.py` |

## Varlıklar (entities/)

| Sayfa | Özet |
|---|---|
| [catboost](entities/catboost.md) | Gradient boosting ML kütüphanesi — talep tahmini + iptal olasılığı tahmini |
| [topsis](entities/topsis.md) | Çok kriterli karar verme yöntemi — teknisyen sıralama + iş emri önceliklendirme |
| [gurobi_mip_cozucusu](entities/gurobi_mip_cozucusu.md) | Exact MIP çözücüsü, 10-13 düğümde tıkanma sorunu |
| [python_gurobipy](entities/python_gurobipy.md) | Python + gurobipy entegrasyonu |
| [model_karar_degiskenleri_ve_parametreleri](entities/model_karar_degiskenleri_ve_parametreleri.md) | Karar değişkenleri/parametreler — kod-doğrulanmış genel bakış tablosu + **Faz 2 uygulama tablosu (7 sorun kodu)** |
| [build_model_fonksiyonu](entities/build_model_fonksiyonu.md) | CV vs EV `build_model()` imza/kapsam karşılaştırması |
| [format_time_fonksiyonu](entities/format_time_fonksiyonu.md) | Saniye→saat formatlama (+28800 kayması) |
| [cozum_raporlama_fonksiyonlari](entities/cozum_raporlama_fonksiyonlari.md) | `print_cv_solution`, `print_ev_solution` |
| [degisken_x_arc_tahsisi](entities/degisken_x_arc_tahsisi.md) | `x[i,j,v,t]` (raw) — **Faz 2'de `src/`'de 3B `x[i,j,k]`'ya indirgendi** |
| [degisken_yakit_enerji_izleme](entities/degisken_yakit_enerji_izleme.md) | `yc/YC` (CV) vs `ye/YE` (EV) — **Faz 2'de `(Np,K)` çok-indisli oldu, A1 şarj bug'ı düzeltildi** |
| [parametre_big_m_100000](entities/parametre_big_m_100000.md) | Sabit `100000.0` (raw) — **Faz 2'de `src/`'de tight-M formülleriyle değiştirildi** |
| [parametre_mola_zaman_sabitleri](entities/parametre_mola_zaman_sabitleri.md) | `break_duration/min/max` sabitleri |
| [birlesik_k_indeksi_ve_yardimci_haritalar](entities/birlesik_k_indeksi_ve_yardimci_haritalar.md) | **Yeni (Faz 2):** `K_pairs`/`KK`/`XK`/`arc_ks`/`out_nodes`/`in_nodes` — 3B `x[i,j,k]` indeksleme altyapısı (yalnızca `src/`) |
| [degisken_z_arac_ekip_atama](entities/degisken_z_arac_ekip_atama.md) | **Yeni (v1.1):** `z`/`z_veh` — araç-ekip atama, CV-27/28 ve EV-22/23 tekillik kısıtlarının temeli |
| [kk_name_degisken_temiz_isimlendirme](entities/kk_name_degisken_temiz_isimlendirme.md) | **Yeni (v1.1):** `.lp` yazımını kıran ham tuple isim sorununun düzeltmesi |
| [solution_validator_fonksiyonlari](entities/solution_validator_fonksiyonlari.md) | **Yeni (v1.1):** `validate_solution`/`summarize_trips` — sefer sırası + araç çakışması doğrulayıcısı |

## Kavramlar (concepts/)

| Sayfa | Özet |
|---|---|
| [colored_tsp](concepts/colored_tsp.md) | Renkli TSP — uyumluluk/yetkinlik temelli araç-müşteri eşleşmesi — **Faz 2'de indeks indirgeme uygulandı** |
| [index_reduction_3b](concepts/index_reduction_3b.md) | 4B→3B karar değişkeni indirgeme tekniği — **Faz 2'de uygulandı (src/)** |
| [tight_big_m](concepts/tight_big_m.md) | Big-M sıkılaştırma tekniği — **Faz 2'de uygulandı (src/), C2** |
| [partial_recharging](concepts/partial_recharging.md) | EV kısmi şarj modellemesi — **Faz 2: A1 etkisizlik bug'ı düzeltildi, tam eşitlik hâlâ eksik** |
| [q_learning](concepts/q_learning.md) | Pekiştirmeli öğrenme tabanlı meta-sezgisel bileşen |
| [vnd](concepts/vnd.md) | Değişken Komşuluk İnişi — rota içi iyileştirme |
| [rolling_horizon](concepts/rolling_horizon.md) | Yuvarlanan ufuk — haftalık/günlük geri bildirim döngüsü |
| [uyumluluk_matrisi](concepts/uyumluluk_matrisi.md) | Teknisyen-araç-görev uyumluluk kısıtı — **Faz 2'de `_crew_allowed()` filtresi olarak uygulandı (A5)** |
| [warm_start](concepts/warm_start.md) | Sweep/K-Means ile hızlı başlangıç rotası üretimi |
| [pareto_epsilon_constraint](concepts/pareto_epsilon_constraint.md) | CV vs EV çok amaçlı Pareto analizi, ε-Constraint yöntemi |
| [klon_dugum_node_replication](concepts/klon_dugum_node_replication.md) | Şarj istasyonu için klonlanmış düğüm tekniği |
| [iptal_olasiligi_tahmini](concepts/iptal_olasiligi_tahmini.md) | ML tabanlı iptal olasılığı ön-filtreleme |
| [literatur_alternatif_metasezgiseller](concepts/literatur_alternatif_metasezgiseller.md) | VLSN, ALNS, MTZ, Filtered Beam Search, HSA — literatür referans yöntemleri |

## Kararlar (decisions/)

**Çelişkiler:**
| Sayfa | Özet |
|---|---|
| [celiski_single_trip_vs_multitrip](decisions/celiski_single_trip_vs_multitrip.md) | **ÇÖZÜLDÜ (2026-08-22):** v1.1 kodu artık gerçekten çoklu sefer (CV-4/EV-4, ≤3) uyguluyor — docx'ün 2026-08-09 iddiasıyla örtüşüyor |
| [celiski_ogle_molasi_zorunlulugu](decisions/celiski_ogle_molasi_zorunlulugu.md) | **ÇÖZÜLDÜ (2026-08-22, kısmen):** yeni matematiksel model belgesi CV kuralını (opsiyonel, CV-13) kodun gerçek davranışına göre yeniden tanımladı; EV zaten tutarlıydı (zorunlu, EV-12) |

**Sorunlar / eksiklikler:**
| Sayfa | Özet |
|---|---|
| [sorun_sarj_yakit_istasyonlari_kodda_yok](decisions/sorun_sarj_yakit_istasyonlari_kodda_yok.md) | CV'de doğrulandı (yok, Faz 2'de de değişmedi); EV'de kısmen var — **Faz 2'de gerçekten çalışır hâle geldi (A1)** |
| [sorun_kismi_sarj_dinamikleri_kodda_yok](decisions/sorun_kismi_sarj_dinamikleri_kodda_yok.md) | EV'de kısmi şarj süresi mekanizması bulundu (`charge_time_i`) — docx iddiası nüanslandı |
| [sorun_hardcoded_mola_parametreleri](decisions/sorun_hardcoded_mola_parametreleri.md) | Mola parametreleri sabit kodlanmış — satır referanslarıyla doğrulandı |
| [sorun_ev_enerji_tuketim_modeli_basitlestirilmis](decisions/sorun_ev_enerji_tuketim_modeli_basitlestirilmis.md) | EV enerji tüketimi hâlâ mesafeye doğrusal bağlı — doğrulandı, **Faz 2'de EV tarafında çözülmedi** (paralel CV sorunu A7 çözüldü) |
| [sorun_cv_kullanilmayan_istasyon_parametreleri](decisions/sorun_cv_kullanilmayan_istasyon_parametreleri.md) | CV'de `Fc`, `alpha`, `g_c`, `k`, `lc0` hiç kullanılmıyor — yarım kalmış istasyon iskeleti (Faz 2'de değişmedi, ilgili A7 tüketim oranı sorunu çözüldü) |
| [sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi](decisions/sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi.md) | **Yeni (Faz 2):** A1 sonrası `ye`/`YE` hâlâ eşitsizlik (eşitlik değil) → raporlanan şarj miktarı şişiyor (~250 yerine 851) |
| [sorun_tau_ub_istasyon_depo_ufuk_sapmasi](decisions/sorun_tau_ub_istasyon_depo_ufuk_sapmasi.md) | **Yeni (Faz 2):** istasyon/depo `tau_ub` artık vardiya ufkuyla sınırlı — ürün kararı bekliyor |
| [sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi](decisions/sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi.md) | **v1.1, kritik — DOĞRULANDI ve ÇÖZÜLDÜ (2026-08-22):** A1 ve A7 regresyonları Gurobi ile kanıtlandı, `raw/`'da doğrudan düzeltildi |
| [sorun_ev_depo_yaylarinda_dongusel_infeasibility](decisions/sorun_ev_depo_yaylarinda_dongusel_infeasibility.md) | **Ölümcül, çözüldü:** EV-17/18/19'un depo yaylarını kapsaması EV modelini HER rota için infeasible yapıyordu (IIS kanıtı) |
| [sorun_ev17_big_m_gecersiz_kucuk](decisions/sorun_ev17_big_m_gecersiz_kucuk.md) | **Çözüldü:** EV-17'nin Big-M'i (`lc_0 + g_e·Q` = 18181.8) geçerlilik sınırının (40581.8) altındaydı, fizibıl çizelgeleri kesiyordu |
| [sorun_coklu_sefer_zaman_sirasi_ihlali](decisions/sorun_coklu_sefer_zaman_sirasi_ihlali.md) | **ÇÖZÜLDÜ (2026-08-23):** CV-26/EV-21 geri alınması zararsız DEĞİLDİ; depo klon düğümleri + CV-29/30/31 & EV-28/29/30 ile giderildi, R10/RC10 artık `valid=True` |
| [sorun_rapor_mola_suresi_3600_vs_ll_el](decisions/sorun_rapor_mola_suresi_3600_vs_ll_el.md) | **Çözüldü:** rapor molayı 1 saat sayıyordu, model `ll−el` = 2 saat ayırıyor (docx model tarafını doğruluyor) |
| [sorun_rapor_unicode_cokme_log_print](decisions/sorun_rapor_unicode_cokme_log_print.md) | **Çözüldü:** emoji içeren rapor cp1254 konsolda çözüm bulunduktan SONRA `UnicodeEncodeError` ile çöküyordu |
| [sorun_rc13_darbogaz_kok_neden_analizi](decisions/sorun_rc13_darbogaz_kok_neden_analizi.md) | **TEŞHİS (2026-08-27), Ö1+Ö2+Ö6 UYGULANDI (2026-08-28):** RC13'ün kök nedeni **LP gevşetmesinde depo bağlantısının hiç zorlanmaması** (LP'de `Σ x[O_r,j,k] = 0`, tüm müşteriler 2-döngüyle kaplanıyor) — CV+EV 14 koşumda evrensel. `raw/` eşdeğeri 900 s'de fizibil çözüm bile bulamıyordu; bkz. [[karar_rc13_asgari_paket_uygulamasi]] için gerçek uygulama sonucu |
| [karar_rc13_asgari_paket_uygulamasi](decisions/karar_rc13_asgari_paket_uygulamasi.md) | **UYGULANDI (2026-08-28):** Ö1 (yetkinlik filtresi) + Ö2 (homojen filoda araç indisi agregasyonu) + Ö6 (istasyon düşürme) + `sorted(set(...))` düzeltmesi `raw/`'a işlendi. RC13 (CV+EV) 900 s/0-çözümden **~67-106 s'de kanıtlanmış optimale** (20667.0); R10/RC10 artık <1 s'de kanıtlanmış optimal (RC10 EV'de yeni en iyi değer: 10729.2). §6'daki "2.7 s" iddiası YANLIŞ karakterize edilmişti — düzeltildi (gerçek rakam Ö3/Ö4/Ö7'yi de gerektiriyordu) |
| [karar_rc13_tam_paket_uygulamasi](decisions/karar_rc13_tam_paket_uygulamasi.md) | **UYGULANDI (2026-08-29):** Ö3 (min_veh, EV) + Ö4 (bwp EV / arc_fix CV+EV) + Ö7a (düğüm-bazlı sıkı Big-M) + Ö7b (ölü kısıt temizliği) + Ö8 (EV mola/şarj çakışması düzeltmesi) `raw/`'a işlendi; Ö5 (statik DFJ) Eren'in talimatıyla rafa kaldırıldı. RC13 EV 5.96 s'de optimal (67.4s'den), CV 36.95s; RC15 EV 11.35 s'de optimal (önceden kanıtlanamıyordu); RC20 hâlâ 0 çözüm (300s) — sınır aşılamadı. **§9.1 ÇELİŞKİ (2026-08-31): RC20 teşhisi ÇÜRÜTÜLDÜ — model INFEASIBLE'dır**, bkz. [[sorun_rc20_darbogaz_kok_neden_analizi]]. **GÜNCELLEME (2026-08-31): bu sayfanın RC13/RC15 rakamları [[karar_5_8_teknisyen_bug_fix]] sonrası GEÇERSİZ** — güncel: RC13 EV **19938.07** (12.87s), RC15 EV **21851.58** (32.15s), her ikisi de **daha iyi** objektif |
| [sorun_rc20_darbogaz_kok_neden_analizi](decisions/sorun_rc20_darbogaz_kok_neden_analizi.md) | **TEŞHİS (2026-08-31) — RC20 ÇÖZÜLEMİYOR DEĞİL, INFEASIBLE (düzeltme ÖNCESİ):** `skill_tech_map[skill][0]` (8 teknisyenin 5'i) + EV-22/CV-27 (`Σz ≤ |V|=3`) + EV-23/CV-28 → zorunlu `{2,2,1}` beceri bölünmesi; 15 bölünmenin **15'i de** aktif kaynak başına 25 200 s'lik günlük hizmet kapasitesini aşıyor (en iyisi **+791 s**). Gurobi, değiştirilmemiş `raw/` modeline tek bir *geçerli* eşitsizlik eklendiğinde infeasibility'yi EV'de **2.5 s**, CV'de **8.0 s**'de kanıtlıyor (aynı eşitsizlik RC13/RC15/R15/C15 optimallerini değiştirmiyor). **n ≥ 20 olan 15 örneğin tamamı infeasible → exact modelin çözebileceği en büyük boyut n = 15 (bug fix öncesi ölçüm).** Ö-B (filo 3→4) RC20'yi %9,35 gap'e taşıyor. **GÜNCELLEME (2026-08-31): Ö-A (5/8 teknisyen bug fix) `raw/`'a UYGULANDI**, bkz. [[karar_5_8_teknisyen_bug_fix]] — RC20 artık infeasible değil (900s'de hâlâ 0 çözüm ama fizibil), Ö-B/Ö-C/Ö-D hâlâ uygulanmadı |
| [karar_5_8_teknisyen_bug_fix](decisions/karar_5_8_teknisyen_bug_fix.md) | **UYGULANDI (2026-08-31):** `skill_tech_map[skill][0]` (yalnızca ilk teknisyen) → tüm teknisyenler döngüsü. `raw/Info4Employee.xml`'deki 8 teknisyenin 3'ü (TECH_002/004/006) hiç kullanılmıyordu. Bug fix (veri/senaryo değişikliği değil) — fizibil çözüm kümesi yalnızca BÜYÜR, objektif asla kötüleşmez. C5 CV değişmedi (8291.18) ama **RC13/RC15 EV gerçekten iyileşti**: RC13 19938.07 (eski 20666.99'dan **%3,5 iyi**), RC15 21851.58 (eski 23912.82'den **%8,6 iyi**) — demek ki önceki "optimal" değerler eksik girdiyle (5 teknisyen) doğruydu, gerçek problemin optimali değildi |

**Kod-only kararlar (modelde/yönergede olmayan, kodun eklediği):**
| Sayfa | Özet |
|---|---|
| [karar_dinamik_teknisyen_ekibi_itertools_combinations](decisions/karar_dinamik_teknisyen_ekibi_itertools_combinations.md) | İkili ekip oluşturma (itertools.combinations) |
| [karar_molasiz_erken_donus_kurali_kod](decisions/karar_molasiz_erken_donus_kurali_kod.md) | Mola kullanılmazsa erken dönüş zorunluluğu |
| [karar_operasyonel_zaman_kaydirma_format_time](decisions/karar_operasyonel_zaman_kaydirma_format_time.md) | +28800 saniye ile 08:00 referans kaydırması |

**Planlanan mimari kararlar:**
| Sayfa | Özet |
|---|---|
| [karar_4b_to_3b_index_reduction_plani](decisions/karar_4b_to_3b_index_reduction_plani.md) | 4B→3B karar değişkeni indirgeme planı — **Faz 2'de src/'de uygulandı (C1)** |
| [karar_tight_big_m_gecisi_plani](decisions/karar_tight_big_m_gecisi_plani.md) | Dinamik Big-M'e geçiş planı — **Faz 2'de src/'de uygulandı (C2), CV+EV** |
| [karar_partial_charging_denklemleri_entegrasyonu_plani](decisions/karar_partial_charging_denklemleri_entegrasyonu_plani.md) | Keskin & Çatay (2016) denklemlerinin entegrasyonu — **Faz 2'de KISMEN uygulandı (A1 düzeltildi, tam eşitlik hâlâ eksik)** |
| [karar_klon_dugum_sarj_istasyonu_plani](decisions/karar_klon_dugum_sarj_istasyonu_plani.md) | Şarj istasyonu klon düğüm planı |
| [karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani](decisions/karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani.md) | **UYGULANDI (2026-08-23):** DEPO klon düğümleriyle sefer-indeksli `τ` (CV-29/30/31, EV-28/29/30) + `u[r,k]` + mola tabanı `z`'ye çevrildi — `raw/`'a işlendi, C5/R5/RC5/R10/RC10 (+EV RC13) CV+EV `valid=True` (§13); §8.3 mitigasyonu 2026-08-24'te uygulandı, §13.2.1'in "RC13 `R_max` mitigasyonu operasyonel gerekliliktir" çıkarımına **ÇELİŞKİ** notu düşüldü |
| [karar_r_max_dinamik_turetme](decisions/karar_r_max_dinamik_turetme.md) | **UYGULANDI (2026-08-24):** `R_max` sabit 3 yerine `derive_r_max()` ile veriden türetiliyor — kanıt "birleştirme baskınlığı + enerji testi"; 27/27 örnekte `R_max=1`, objektif değişmedi (C5/R5/RC5 × CV+EV), CV `NumVars` %-39.6 / EV %-26.8; RC13'te hız kazancı **doğrulanamadı** (§9.1) |
| [karar_uyumluluk_matrisi_cizelgeleme_plani](decisions/karar_uyumluluk_matrisi_cizelgeleme_plani.md) | Uyumluluk matrisinin yeni bölüm olarak eklenmesi |
| [karar_gunluk_haftalik_planlama_pool_plani](decisions/karar_gunluk_haftalik_planlama_pool_plani.md) | Haftalık→günlük havuz dağıtım süreci |
| [karar_hibrit_algoritma_mimari_sirasi](decisions/karar_hibrit_algoritma_mimari_sirasi.md) | Kümeleme→Warm-start→B&B→VND+Q-Learning sırası |
| [karar_pareto_epsilon_constraint_plani](decisions/karar_pareto_epsilon_constraint_plani.md) | CV/EV Pareto kıyaslama planı |
| [karar_literatur_temelli_problem_tanimi_md_gctsp_tw](decisions/karar_literatur_temelli_problem_tanimi_md_gctsp_tw.md) | MD-GCTSP-TW olarak problem temellendirme |
| [karar_3_asamali_rolling_horizon_sistem_mimarisi](decisions/karar_3_asamali_rolling_horizon_sistem_mimarisi.md) | 3 aşamalı (haftalık/günlük/rolling horizon) sistem tasarımı |
| [karar_iptal_olasiligi_on_filtreleme_plani](decisions/karar_iptal_olasiligi_on_filtreleme_plani.md) | İptal olasılığı ön filtreleme planı |
| [karar_sentetik_veri_uretici_solomon_plani](decisions/karar_sentetik_veri_uretici_solomon_plani.md) | Solomon-tipi sentetik veri üretici modül planı |
| [karar_3_fazli_uygulama_yol_haritasi](decisions/karar_3_fazli_uygulama_yol_haritasi.md) | Faz 1 (kod)→Faz 2 (sezgisel)→Faz 3 (makale) sıralaması |

**Faz 2 uygulama kararları (2026-08-11, `src/` altında kodlanmış, `raw/` değişmedi):**
| Sayfa | Özet |
|---|---|
| [karar_src_klasoru_ve_raw_izolasyonu](decisions/karar_src_klasoru_ve_raw_izolasyonu.md) | `raw/`→`src/` dosya haritası ve Hard Rule 1 uyum gerekçesi |
| [karar_a1_ev_sarj_c20_c21_duzeltmesi](decisions/karar_a1_ev_sarj_c20_c21_duzeltmesi.md) | A1: EV `c20`'nin `c21`'i ezip şarjı etkisizleştirmesi düzeltildi |
| [karar_a7_cv_yakit_tuketim_orani_duzeltmesi](decisions/karar_a7_cv_yakit_tuketim_orani_duzeltmesi.md) | A7: CV `h_c=1.0` sabiti yerine `EnergyConsumptionRate` XML'den okunuyor |
| [karar_a6_cv_non_overlap_portlamasi](decisions/karar_a6_cv_non_overlap_portlamasi.md) | A6: EV teknisyen çakışma önleme mekanizması CV'ye portlandı |
| [karar_a4_zaman_penceresi_bigm_kosullandirma](decisions/karar_a4_zaman_penceresi_bigm_kosullandirma.md) | A4: `c16/c17/c18` hibrit Big-M koşullandırması (infeasibility riski giderildi) |
| [karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme](decisions/karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme.md) | A2+C1+A5: birleşik `k`=(araç,ekip) indeksi, çok-indisli enerji izleme, yetkinlik filtresi — en riskli/kapsamlı değişiklik |
| [karar_c2_tight_big_m_uygulamasi](decisions/karar_c2_tight_big_m_uygulamasi.md) | C2: 4 kısıt grubunda sabit `100000.0` → türetilmiş M, sapma notu (`-ec[j]` neden kullanılmadı) |

**v1.1 kararları (2026-08-22, `raw/`'un kendisi Eren onayıyla tamamen yeniden yazıldı — Hard Rule §7.1'in bilinçli istisnası):**
| Sayfa | Özet |
|---|---|
| [karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari](decisions/karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari.md) | CV-4/EV-4 (≤3 çoklu sefer, artık gerçek), `z`/`z_veh` + CV-27/28, EV-22/23 (araç-ekip/teknisyen tekilliği) — `solution_validator.py` ile bulunan RC7/CV_3 araç çakışması hatasının düzeltmesi |
| [karar_src_klasoru_ve_raw_izolasyonu](decisions/karar_src_klasoru_ve_raw_izolasyonu.md) | **Güncellendi:** `raw/` tabanı değişti, `src/*_fixed.py` artık eski bir tabana dayanıyor — merkezi hub notu |
| [sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi](decisions/sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi.md) | **Kritik — DOĞRULANDI/ÇÖZÜLDÜ:** A1 (EV şarj) ve A7 (CV yakıt oranı) regresyonları gerçekti; Gurobi kanıtlarıyla `raw/`'da düzeltildi |
| [sorun_ev_depo_yaylarinda_dongusel_infeasibility](decisions/sorun_ev_depo_yaylarinda_dongusel_infeasibility.md) | **Ölümcül, çözüldü:** EV modeli her rota için infeasible'dı (EV-17/18/19 depo yaylarını kapsıyordu) — ÇELİŞKİ başlığı: docx'in EV bölümünde CV-23/24/25 karşılığı yok |
| [karar_ev_depo_sarj_ve_donus_enerjisi_kisitlari](decisions/karar_ev_depo_sarj_ve_donus_enerjisi_kisitlari.md) | EV-24/25/26/27 eklendi (depoda tam şarj, dönüş enerjisi, müşteride şarj yok) — CV-22/23/24/25 ile simetri |
| [sorun_ev17_big_m_gecersiz_kucuk](decisions/sorun_ev17_big_m_gecersiz_kucuk.md) | EV-17 Big-M geçersizliği (CV'de `lc0=40000` override var, EV'de yok) — `max(lc0, ls−es) + g·Q` ile düzeltildi |
| [sorun_coklu_sefer_zaman_sirasi_ihlali](decisions/sorun_coklu_sefer_zaman_sirasi_ihlali.md) | **ÇÖZÜLDÜ (2026-08-23):** klon düğüm tasarımı `raw/`'a uygulandı; karşıt-olgusal koşum ihlali CV-29'a izole ediyor → [karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani](decisions/karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani.md) |
| [sorun_rapor_mola_suresi_3600_vs_ll_el](decisions/sorun_rapor_mola_suresi_3600_vs_ll_el.md) | Kütüphanecinin "Bulgu 7" mola penceresi şüphesinin yanıtı: model kasıtlı, rapor bug'lıydı |
| [sorun_rapor_unicode_cokme_log_print](decisions/sorun_rapor_unicode_cokme_log_print.md) | `log_print` Unicode çökmesi düzeltildi |

## Sentezler (syntheses/)

| Sayfa | Özet |
|---|---|
| [model_kod_farkliliklari_genel_sentez](syntheses/model_kod_farkliliklari_genel_sentez.md) | Docx'teki 10 farklılık maddesinin Stage 2 kod doğrulamasıyla birleştirilmiş genel değerlendirmesi + makale öncesi önceliklendirme |

## Arşiv (archive/)

2026-08-22'de `raw/CV_model_gurobi_exact.py`, `raw/EV_v.1.1.py`, `raw/xml_data_loader.py`'nin v1.1 ile yeniden yazılması sonucu artık geçerli `raw/` içeriğini tarif etmeyen 7 sayfa önce buraya taşınmış, ardından Eren'in açık isteğiyle **kalıcı olarak silinmiştir** (CLAUDE.md Hard Rule §7.3'ün bilinçli istisnası — bkz. [[karar_src_klasoru_ve_raw_izolasyonu]] GÜNCELLEME notu). Güncel karşılıkları: eski CV/EV kod incelemeleri → [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]] / [[sources/2026-08-22-ev_v1_1_rewrite]]; eski EV teknisyen-çakışma/route_start-end/Gurobi-tuning/docx-raporlama sayfaları → [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]] / [[degisken_z_arac_ekip_atama]] / [[cozum_raporlama_fonksiyonlari]].

`src/*_fixed.py` (Faz 2) dosyaları bu değişiklikten etkilenmedi — hâlâ eski `raw/` tabanına dayanıyorlar (bkz. [[karar_src_klasoru_ve_raw_izolasyonu]]).
