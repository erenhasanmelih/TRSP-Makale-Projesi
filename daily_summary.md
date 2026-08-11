# TRSP Günlük Değişiklik Özeti — 2026-08-11

_Otomatik üretildi: `generate_report.py` | Tarih: 2026-08-11_

## 📋 Bugünkü Log Kayıtları (`log.md`)

### `execution` — Faz 2: Kod Düzeltmeleri (A1-A7, C1-C2) ve Wiki Güncellemesi

Faz 1'de tespit edilen 7 kritik sorun (A1, A7, A6, A4, A2+C1, A5, C2), `raw/` HİÇ DEĞİŞTİRİLMEDEN (Hard Rule 1), kök dizinde yeni açılan `src/` klasörü altında üç kopyada (`src/EV_v_1_1_fixed.py` ← `raw/EV_v.1.1.py`; `src/CV_model_gurobi_fixed.py` ← `raw/CV_model_gurobi_exact.py`; `src/xml_data_loader_fixed.py` ← `raw/xml_data_loader.py`) düzeltildi ve Gurobi 13 ile R5 problem setinde gerçek çözüm alınarak doğrulandı: EV `status=OPTIMAL, obj=10116.10`; CV `status=OPTIMAL, obj=10116.10` (çapraz tutarlı).

Düzeltilen 7 sorun: **A1** (EV `c20`'nin `c21`'i ezip şarjı etkisizleştirmesi), **A7** (CV `h_c=1.0` sabiti yerine `EnergyConsumptionRate` XML'den okunuyor), **A6** (EV teknisyen çakışma önleme CV'ye portlandı), **A4** (`c16/c17/c18` hibrit Big-M koşullandırması, infeasibility riski giderildi), **A2+C1** (4B→3B `x[i,j,k]` indirgeme, birleşik `k`=(araç,ekip) indeksi, çok-indisli enerji izleme — en riskli/kapsamlı değişiklik), **A5** (yetkinlik filtresi `_crew_allowed`, A2+C1 refaktörüyle birlikte), **C2** (4 kısıt grubunda sabit `100000.0` → türetilmiş tight Big-M).

**Bu wiki dokunuşu (kütüphaneci operasyonu):**

Güncellenen mevcut sayfalar (11) — her biri orijinal içerik korunarak "## Uygulama (Faz 2, 2026-08-11)" bölümü eklendi, hiçbiri silinmedi:
- decisions/karar_4b_to_3b_index_reduction_plani.md — plan → uygulandı
- decisions/karar_tight_big_m_gecisi_plani.md — plan → uygulandı (CV+EV)
- decisions/karar_partial_charging_denklemleri_entegrasyonu_plani.md — KISMEN uygulandı (A1 düzeltildi, Keskin & Çatay tam eşitlik hâlâ eksik)
- decisions/karar_ev_teknisyen_cakisma_onleme_mekanizmasi.md — CV'ye portlandığı eklendi
- decisions/sorun_sarj_yakit_istasyonlari_kodda_yok.md — EV tarafı artık gerçekten çalışıyor, CV değişmedi
- decisions/sorun_ev_enerji_tuketim_modeli_basitlestirilmis.md — EV tarafı çözülmedi, ilgili CV sorunu (A7) çözüldü notu eklendi
- decisions/sorun_cv_kullanilmayan_istasyon_parametreleri.md — A7 ile çapraz-referans eklendi
- decisions/celiski_single_trip_vs_multitrip.md — Faz 2 analizinin de tek-sefer'i doğruladığı not düşüldü, çelişki hâlâ çözülmedi
- entities/parametre_big_m_100000.md — raw'da sabit kaldığı, src'de tight-M olduğu eklendi
- entities/degisken_x_arc_tahsisi.md — raw 4B, src 3B olduğu eklendi
- entities/degisken_yakit_enerji_izleme.md — src'de çok-indisli (Np,K) olduğu + A1 eklendi
- entities/model_karar_degiskenleri_ve_parametreleri.md — 7 sorun kodu uygulama tablosu eklendi
- entities/model_calistirma_parametreleri_ev.md — `resolve_data_root()` eklendi
- concepts/tight_big_m.md, concepts/index_reduction_3b.md, concepts/partial_recharging.md, concepts/colored_tsp.md, concepts/uyumluluk_matrisi.md — Faz 2 uygulama notları eklendi

Yeni açılan atomik sayfalar (11):
- decisions/karar_src_klasoru_ve_raw_izolasyonu.md (yeni)
- decisions/karar_a1_ev_sarj_c20_c21_duzeltmesi.md (yeni)
- decisions/karar_a7_cv_yakit_tuketim_orani_duzeltmesi.md (yeni)
- decisions/karar_a6_cv_non_overlap_portlamasi.md (yeni)
- decisions/karar_a4_zaman_penceresi_bigm_kosullandirma.md (yeni)
- decisions/karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme.md (yeni)
- decisions/karar_c2_tight_big_m_uygulamasi.md (yeni)
- decisions/sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi.md (yeni sorun, kalan iş)
- decisions/sorun_tau_ub_istasyon_depo_ufuk_sapmasi.md (yeni sorun, ürün kararı bekliyor)
- entities/birlesik_k_indeksi_ve_yardimci_haritalar.md (yeni)
- index.md (güncellendi — yeni sayfalar tablolara eklendi, mevcut satırların özetleri Faz 2 durumuna göre tazelendi)

Toplam: 11 mevcut sayfa güncellendi, 10 yeni sayfa açıldı (9 decision + 1 entity), index.md güncellendi.

**Açık/çözülmemiş 2 nokta (kalan iş, kullanıcı kararı bekliyor):**
1. **Raporlama güvenilirliği (`sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi`):** A1 düzeltmesi sonrası `ye`/`YE` hâlâ tek-yönlü `<=` eşitsizlikle bağlı (eşitlik değil) — fizibiliteyi bozmuyor ama `print_ev_solution`'ın raporladığı şarj miktarı şişebiliyor (test: ~250 yerine 851). Çözüm: Keskin & Çatay (2016) tam eşitlik denklemlerinin entegrasyonu — `karar_partial_charging_denklemleri_entegrasyonu_plani.md`'nin kalan işi.
2. **`tau_ub` istasyon/depo ufuk sapması (`sorun_tau_ub_istasyon_depo_ufuk_sapmasi`):** İstasyon/depo düğümlerinde `tau_ub[i]` artık vardiya ufkuyla (`horizon_end`) sınırlı, yükleyicideki yapay `lc=100000` yerine — hafif bir sıkılaştırma, orijinal modelde yoktu. Geri alınabilir ama Big-M gevşer. Ürün kararı bekliyor.

Ayrıca lint-report-2026-08-09.md'deki C1 bulgusu (partial_charging plan sayfasının eski Gerekçe metniyle güncel bilgi arasındaki çelişki) bu operasyonda fiilen çözüldü — plan sayfası artık "KISMEN uygulandı" durumunu ve kalan işi net biçimde yansıtıyor.

## 📁 Bugün Eklenen/Güncellenen Karar Sayfaları (`decisions/`)

| Sayfa | Başlık | Durum |
|---|---|---|
| `decisions/celiski_single_trip_vs_multitrip.md` | ÇELİŞKİ — Single-Trip (Model) vs Multi-Trip (Kod) | güncel |
| `decisions/karar_4b_to_3b_index_reduction_plani.md` | Karar (Planlı) — 4B'den 3B'ye İndis Düşürme | güncel |
| `decisions/karar_a1_ev_sarj_c20_c21_duzeltmesi.md` | Karar (Faz 2, A1) — EV Şarj c20/c21 Çakışması Düzeltmesi | güncel |
| `decisions/karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme.md` | Karar (Faz 2, A2+C1) — Birleşik k İndeksi ve Enerji/Yakıt İzlemenin Çok-İndisli Hale Getirilmesi | güncel |
| `decisions/karar_a4_zaman_penceresi_bigm_kosullandirma.md` | Karar (Faz 2, A4) — Zaman Penceresi Big-M Koşullandırması (Hibrit Yaklaşım) | güncel |
| `decisions/karar_a6_cv_non_overlap_portlamasi.md` | Karar (Faz 2, A6) — EV Teknisyen Çakışma Önlemenin CV'ye Portlanması | güncel |
| `decisions/karar_a7_cv_yakit_tuketim_orani_duzeltmesi.md` | Karar (Faz 2, A7) — CV Yakıt Tüketim Oranı Düzeltmesi | güncel |
| `decisions/karar_c2_tight_big_m_uygulamasi.md` | Karar (Faz 2, C2) — Tight Big-M Uygulaması | güncel |
| `decisions/karar_ev_teknisyen_cakisma_onleme_mekanizmasi.md` | Karar (Kod, EV) — Teknisyen Çakışma Önleme Mekanizması | güncel |
| `decisions/karar_partial_charging_denklemleri_entegrasyonu_plani.md` | Karar (Planlı) — Partial Charging Denklemlerinin Entegrasyonu | güncel |
| `decisions/karar_src_klasoru_ve_raw_izolasyonu.md` | Karar (Faz 2) — src/ Klasörü ve raw/ İzolasyonu | güncel |
| `decisions/karar_tight_big_m_gecisi_plani.md` | Karar (Planlı) — Sıkı Big-M'e Geçiş | güncel |
| `decisions/sorun_cv_kullanilmayan_istasyon_parametreleri.md` | Sorun (Kod, CV) — Kullanılmayan İstasyon-İlişkili Parametreler (Fc, alpha, g_c, k, lc0) | güncel |
| `decisions/sorun_ev_enerji_tuketim_modeli_basitlestirilmis.md` | Sorun — EV Enerji Tüketim Modeli Aşırı Basitleştirilmiş | güncel |
| `decisions/sorun_sarj_yakit_istasyonlari_kodda_yok.md` | Sorun — Şarj/Yakıt İstasyonları ve Mola-İstasyon Bağıntıları Kodda Yok | güncel |
| `decisions/sorun_tau_ub_istasyon_depo_ufuk_sapmasi.md` | Sorun (Faz 2, Küçük) — tau_ub İstasyon/Depo Ufuk Sapması | güncel |
| `decisions/sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi.md` | Sorun (Faz 2, Kalan İş) — ye/YE Eşitsizlik Kısmi Şarj Raporlama Hatası | güncel |

---

_Bu rapor TRSP Proje Koordinatörü ajanı tarafından tetiklenmiştir._