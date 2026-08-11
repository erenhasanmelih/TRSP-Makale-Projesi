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
| [2026-08-09-cv_model_gurobi_exact](sources/2026-08-09-cv_model_gurobi_exact.md) | CV exact MIP kod incelemesi — `build_model`, kısıtlar, tek-sefer doğrulaması, kullanılmayan istasyon parametreleri | `raw/CV_model_gurobi_exact.py` |
| [2026-08-09-ev_v1_1](sources/2026-08-09-ev_v1_1.md) | EV exact MIP kod incelemesi — istasyon/şarj kısıtları, teknisyen çakışma önleme, otomatik docx raporlama | `raw/EV_v.1.1.py` |

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
| [degisken_route_start_route_end_ev](entities/degisken_route_start_route_end_ev.md) | EV'ye özgü ekip çakışma önleme değişkenleri — **Faz 2'de CV'ye portlandı** |
| [model_calistirma_parametreleri_ev](entities/model_calistirma_parametreleri_ev.md) | EV modül-seviyesi bayraklar + Gurobi tuning parametreleri + `resolve_data_root()` (Faz 2) |
| [birlesik_k_indeksi_ve_yardimci_haritalar](entities/birlesik_k_indeksi_ve_yardimci_haritalar.md) | **Yeni (Faz 2):** `K_pairs`/`KK`/`XK`/`arc_ks`/`out_nodes`/`in_nodes` — 3B `x[i,j,k]` indeksleme altyapısı |

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
| [celiski_single_trip_vs_multitrip](decisions/celiski_single_trip_vs_multitrip.md) | Model: tek çıkış / Docx: kodda 3 tura kadar iddiası — Stage 2 ve Faz 2 analizinde kodda **doğrulanamadı** (2 bağımsız okuma), kod tek-sefer; hâlâ çözülmemiş docx↔kod çelişkisi |
| [celiski_ogle_molasi_zorunlulugu](decisions/celiski_ogle_molasi_zorunlulugu.md) | Model: mola zorunlu (`=1`) vs Kod: opsiyonel (`<=1`) — Stage 2'de kodla doğrulandı |

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

**Kod-only kararlar (modelde/yönergede olmayan, kodun eklediği):**
| Sayfa | Özet |
|---|---|
| [karar_dinamik_teknisyen_ekibi_itertools_combinations](decisions/karar_dinamik_teknisyen_ekibi_itertools_combinations.md) | İkili ekip oluşturma (itertools.combinations) |
| [karar_molasiz_erken_donus_kurali_kod](decisions/karar_molasiz_erken_donus_kurali_kod.md) | Mola kullanılmazsa erken dönüş zorunluluğu |
| [karar_operasyonel_zaman_kaydirma_format_time](decisions/karar_operasyonel_zaman_kaydirma_format_time.md) | +28800 saniye ile 08:00 referans kaydırması |
| [karar_ev_teknisyen_cakisma_onleme_mekanizmasi](decisions/karar_ev_teknisyen_cakisma_onleme_mekanizmasi.md) | EV'de aynı teknisyenin birden fazla ekipte çakışmasını önleyen mekanizma — **Faz 2'de CV'ye portlandı (A6)** |
| [karar_ev_feasibility_gurobi_tuning_ve_diagnostik](decisions/karar_ev_feasibility_gurobi_tuning_ve_diagnostik.md) | **Yeni (Stage 2):** EV'ye özgü 12 Gurobi tuning parametresi + IIS diagnostik |
| [karar_ev_otomatik_docx_raporlama](decisions/karar_ev_otomatik_docx_raporlama.md) | **Yeni (Stage 2):** `raw/sonuclar/*.docx` dosyalarının kaynağı — otomatik Tee+docx kaydı |

**Planlanan mimari kararlar:**
| Sayfa | Özet |
|---|---|
| [karar_4b_to_3b_index_reduction_plani](decisions/karar_4b_to_3b_index_reduction_plani.md) | 4B→3B karar değişkeni indirgeme planı — **Faz 2'de src/'de uygulandı (C1)** |
| [karar_tight_big_m_gecisi_plani](decisions/karar_tight_big_m_gecisi_plani.md) | Dinamik Big-M'e geçiş planı — **Faz 2'de src/'de uygulandı (C2), CV+EV** |
| [karar_partial_charging_denklemleri_entegrasyonu_plani](decisions/karar_partial_charging_denklemleri_entegrasyonu_plani.md) | Keskin & Çatay (2016) denklemlerinin entegrasyonu — **Faz 2'de KISMEN uygulandı (A1 düzeltildi, tam eşitlik hâlâ eksik)** |
| [karar_klon_dugum_sarj_istasyonu_plani](decisions/karar_klon_dugum_sarj_istasyonu_plani.md) | Şarj istasyonu klon düğüm planı |
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

## Sentezler (syntheses/)

| Sayfa | Özet |
|---|---|
| [model_kod_farkliliklari_genel_sentez](syntheses/model_kod_farkliliklari_genel_sentez.md) | Docx'teki 10 farklılık maddesinin Stage 2 kod doğrulamasıyla birleştirilmiş genel değerlendirmesi + makale öncesi önceliklendirme |

## Arşiv (archive/)

_Henüz arşivlenmiş sayfa yok._
