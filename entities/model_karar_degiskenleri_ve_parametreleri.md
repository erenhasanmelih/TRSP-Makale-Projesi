---
title: Model Karar Değişkenleri ve Parametreleri (Genel Bakış)
tags: [entity, mip, karar-değişkeni, parametre, genel-bakış]
source: raw/Yönergelerimiz/Full Path.docx; raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx; raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Model Karar Değişkenleri ve Parametreleri (Genel Bakış)

Bu sayfa, yönerge belgelerinde ve kodda adı geçen karar değişkenlerinin ve parametrelerin üst düzey envanteridir. Kod seviyesindeki tam tanımlar Stage 2 ingest'inde (`CV_model_gurobi_exact.py`, `EV_v.1.1.py`) doğrulandı — detaylı sayfalar için aşağıdaki tabloya ve [[degisken_x_arc_tahsisi]], [[degisken_yakit_enerji_izleme]], [[parametre_big_m_100000]], [[parametre_mola_zaman_sabitleri]], degisken_route_start_route_end_ev (silindi) sayfalarına bakın.

## Planlanan / tartışılan değişkenler ve parametreler

| Sembol / ad | Anlamı | Durum |
|---|---|---|
| 4B karar değişkeni (çıkış, varış, araç, ekip) | Mevcut model formülasyonu | [[karar_4b_to_3b_index_reduction_plani]] ile 3B'ye indirgenmesi planlanıyor |
| 3B karar değişkeni (çıkış, varış, uyumlu araç-ekip kaynağı) | Planlanan yeni formülasyon | Henüz kodda değil |
| Big-M (`100000.0`) | Zaman ilerlemesi / dönüş kısıtlarında sabit büyük sayı | [[tight_big_m]] ile dinamikleştirilmesi planlanıyor |
| F (şarj/yakıt istasyonları kümesi) | Matematiksel modelde tanımlı | CV kodunda yok (`Fc`/`alpha` kullanılmıyor); EV kodunda `S`/`S_set` olarak **var ve aktif** — bkz. [[sorun_sarj_yakit_istasyonlari_kodda_yok]] |
| Şarj hızı katsayısı (`g_e`), dolum süresi | Kısıt (17), (19) | EV kodunda kısmen var (`charge_time_i` terimi, `c8_zaman_ilerleme`) — bkz. [[sorun_kismi_sarj_dinamikleri_kodda_yok]] |
| Renk/Yetkinlik Matrisi (deterministik parametre) | Teknisyen-araç-görev uyumluluğu | Kodda Python seviyesinde (`Ti[j]`) filtreleme olarak var, Gurobi kısıtı olarak değil — bkz. [[karar_uyumluluk_matrisi_cizelgeleme_plani]] |
| Mola parametreleri (esnek) | Model tarafında parametrik | Kodda hardcoded (`break_duration=3600`, `break_min=13800`, `break_max=15000`) — bkz. [[parametre_mola_zaman_sabitleri]], [[sorun_hardcoded_mola_parametreleri]] |

## Kod-doğrulanmış karar değişkenleri (Stage 2)

| Değişken | CV | EV | Sayfa |
|---|---|---|---|
| Arc tahsisi | `x[i,j,v,t]` | `x[i,j,v,t]` | [[degisken_x_arc_tahsisi]] |
| Varış zamanı | `tau[i,t]` | `tau[i,t]` | — |
| Mola indikatörü | `w[i,j,t]` | `w[i,j,t]` | — |
| Yakıt/enerji | `yc`/`YC` | `ye`/`YE` | [[degisken_yakit_enerji_izleme]] |
| Ekip rota göstergesi | yok | `y_route[t]` | 2026-08-09-ev_v1_1 (silindi) |
| Ekip çakışma önleme | yok | `route_start`/`route_end`/`ord_*` | degisken_route_start_route_end_ev (silindi) |
| Kullanılmayan | `L[i,t]`, `alpha[Fc,Vc]` | `L[i,t]` | [[sorun_cv_kullanilmayan_istasyon_parametreleri]] |

## Faz 2 uygulama tablosu (2026-08-11) — `src/EV_v_1_1_fixed.py` / `src/CV_model_gurobi_fixed.py`

`raw/` değişmedi (Hard Rule 1); aşağıdaki tablo yukarıdaki "planlanan" satırların hangilerinin `src/` altında gerçekten koda döküldüğünü özetliyor. Her satırın atomik kaydı ilgili `decisions/karar_a*`/`karar_c*` sayfasında.

| Sorun kodu | Konu | Durum | Sayfa |
|---|---|---|---|
| C1 | 4B→3B `x[i,j,k]` indirgeme + birleşik `k`=(araç,ekip) | Uygulandı | [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]] |
| C2 | Sabit `100000.0` → tight/dinamik Big-M | Uygulandı (4 kısıt grubu) | [[karar_c2_tight_big_m_uygulamasi]] |
| A1 | EV `c20`'nin `c21`'i ezmesi (şarj etkisizliği) | Uygulandı | [[karar_a1_ev_sarj_c20_c21_duzeltmesi]] |
| A7 | CV `h_c=1.0` sabiti, `EnergyConsumptionRate` okunmuyordu | Uygulandı | [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]] |
| A6 | EV teknisyen çakışma önleme CV'de yoktu | CV'ye portlandı | [[karar_a6_cv_non_overlap_portlamasi]] |
| A4 | `c16/c17/c18` koşulsuz Big-M (infeasibility riski) | Hibrit koşullandırma uygulandı | [[karar_a4_zaman_penceresi_bigm_kosullandirma]] |
| A5 | Yetkinlik filtresi | C1 refaktörüyle birlikte uygulandı | [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]] |
| — | Keskin & Çatay tam eşitlik denklemleri | **Hâlâ eksik** (kısmen) | [[karar_partial_charging_denklemleri_entegrasyonu_plani]], [[sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi]] |
| — | `tau_ub[i]` istasyon/depo ufuk sapması | Yeni, ürün kararı bekliyor | [[sorun_tau_ub_istasyon_depo_ufuk_sapmasi]] |

Doğrulama: R5 problem setinde Gurobi 13 ile OPTIMAL çözüm (EV: obj=10116.10, CV: obj=10116.10). Kod haritası ve `raw/` izolasyon gerekçesi: [[karar_src_klasoru_ve_raw_izolasyonu]].

## v1.1 uygulama tablosu (2026-08-22) — raw/'un kendisi (src/'den bağımsız)

`raw/CV_model_gurobi_exact.py`/`raw/EV_v.1.1.py`'nin 2026-08-22 yeniden yazımı, Faz 2 uygulama tablosundaki bazı "planlanan" satırları `src/`'den **bağımsız olarak** `raw/`'un kendisinde de fiilen ele aldı — ama farklı bir mekanizmayla ve bazı Faz 2 kazanımlarını miras almadan:

| Konu | v1.1 raw/ durumu | Faz 2 (src/) ile ilişki |
|---|---|---|
| 4B→3B `x[i,j,k]` | Uygulandı (`kk` tuple, `kk_name`) | Kavramsal olarak aynı, bağımsız uygulama |
| Sabit `100000.0` Big-M | Kaldırıldı, tight-M formülleri | Kavramsal olarak aynı, bağımsız uygulama |
| Çoklu sefer (≤3) | **Yeni** — hem CV hem EV'de (CV-4/EV-4) | Faz 2 kapsamında değildi |
| Araç-ekip/teknisyen tekilliği | **Yeni** — `z`/`z_veh`, CV-27/28, EV-22/23 | Faz 2'nin A6'sından farklı mekanizma (zaman-penceresi değil, atama-tekilliği) |
| A1 (EV şarj c20/c21) | **Muhtemelen miras alınmadı** (doğrulanmadı) | Bkz. [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]] |
| A7 (CV h_c sabiti) | **Muhtemelen miras alınmadı** (doğrulanmadı) | Bkz. [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]] |
| A6 (teknisyen çakışma) | Farklı mekanizmayla (z-tabanlı) kapatıldı | `src/CV_model_gurobi_fixed.py`'deki A6 portlaması etkilenmedi |

Detay: [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]], [[karar_src_klasoru_ve_raw_izolasyonu]] (GÜNCELLEME bölümü), [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]], [[sources/2026-08-22-ev_v1_1_rewrite]].

## Sources

- `raw/Yönergelerimiz/Full Path.docx`
- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx`
- `raw/CV_model_gurobi_exact.py`
- `raw/EV_v.1.1.py`
- `src/EV_v_1_1_fixed.py`
- `src/CV_model_gurobi_fixed.py`
- `src/xml_data_loader_fixed.py`

## Related

- [[index_reduction_3b]]
- [[tight_big_m]]
- [[partial_recharging]]
- [[uyumluluk_matrisi]]
- [[gurobi_mip_cozucusu]]
- [[degisken_x_arc_tahsisi]]
- [[degisken_yakit_enerji_izleme]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
- [[karar_c2_tight_big_m_uygulamasi]]
- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
- [[karar_a6_cv_non_overlap_portlamasi]]
- [[karar_a4_zaman_penceresi_bigm_kosullandirma]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
