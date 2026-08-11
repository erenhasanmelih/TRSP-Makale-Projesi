# Log

Append-only zaman damgalı olay kaydı. Her ingest, anlamlı query ve lint pass buraya eklenir. Asla düzenlenmez veya silinmez, sadece sona eklenir.

Format:
```
## [YYYY-MM-DD] ingest | Kaynak adı
## [YYYY-MM-DD] query | "Soru" → filed: syntheses/xxx.md
## [YYYY-MM-DD] lint | N çelişki, N orphan
```

---

## [2026-08-09] setup | Wiki iskeleti kuruldu (sources/, entities/, concepts/, decisions/, syntheses/, archive/, index.md, log.md, CLAUDE.md). raw/ içindeki kaynaklar sayıldı, henüz ingest edilmedi.

## [2026-08-09] ingest | raw/Yönergelerimiz/ — 5 Word yönerge belgesi (Stage 1)

Dokunulan dosyalar:
- sources/2026-08-09-dinamik_tahminleme_adimlari_ve_veri.md (yeni)
- sources/2026-08-09-ek_noktalar_ve_makaleleri.md (yeni)
- sources/2026-08-09-full_path.md (yeni)
- sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar.md (yeni)
- sources/2026-08-09-makale_adimlar_ve_duzenlemeler.md (yeni)
- entities/catboost.md (yeni)
- entities/topsis.md (yeni)
- entities/gurobi_mip_cozucusu.md (yeni)
- entities/python_gurobipy.md (yeni)
- entities/model_karar_degiskenleri_ve_parametreleri.md (yeni)
- concepts/colored_tsp.md (yeni)
- concepts/index_reduction_3b.md (yeni)
- concepts/tight_big_m.md (yeni)
- concepts/partial_recharging.md (yeni)
- concepts/q_learning.md (yeni)
- concepts/vnd.md (yeni)
- concepts/rolling_horizon.md (yeni)
- concepts/uyumluluk_matrisi.md (yeni)
- concepts/warm_start.md (yeni)
- concepts/pareto_epsilon_constraint.md (yeni)
- concepts/klon_dugum_node_replication.md (yeni)
- concepts/iptal_olasiligi_tahmini.md (yeni)
- concepts/literatur_alternatif_metasezgiseller.md (yeni)
- decisions/celiski_single_trip_vs_multitrip.md (yeni, ÇELİŞKİ)
- decisions/celiski_ogle_molasi_zorunlulugu.md (yeni, ÇELİŞKİ)
- decisions/sorun_sarj_yakit_istasyonlari_kodda_yok.md (yeni)
- decisions/sorun_kismi_sarj_dinamikleri_kodda_yok.md (yeni)
- decisions/sorun_hardcoded_mola_parametreleri.md (yeni)
- decisions/sorun_ev_enerji_tuketim_modeli_basitlestirilmis.md (yeni)
- decisions/karar_dinamik_teknisyen_ekibi_itertools_combinations.md (yeni)
- decisions/karar_molasiz_erken_donus_kurali_kod.md (yeni)
- decisions/karar_operasyonel_zaman_kaydirma_format_time.md (yeni)
- decisions/karar_4b_to_3b_index_reduction_plani.md (yeni)
- decisions/karar_tight_big_m_gecisi_plani.md (yeni)
- decisions/karar_partial_charging_denklemleri_entegrasyonu_plani.md (yeni)
- decisions/karar_klon_dugum_sarj_istasyonu_plani.md (yeni)
- decisions/karar_uyumluluk_matrisi_cizelgeleme_plani.md (yeni)
- decisions/karar_gunluk_haftalik_planlama_pool_plani.md (yeni)
- decisions/karar_hibrit_algoritma_mimari_sirasi.md (yeni)
- decisions/karar_pareto_epsilon_constraint_plani.md (yeni)
- decisions/karar_literatur_temelli_problem_tanimi_md_gctsp_tw.md (yeni)
- decisions/karar_3_asamali_rolling_horizon_sistem_mimarisi.md (yeni)
- decisions/karar_iptal_olasiligi_on_filtreleme_plani.md (yeni)
- decisions/karar_sentetik_veri_uretici_solomon_plani.md (yeni)
- decisions/karar_3_fazli_uygulama_yol_haritasi.md (yeni)
- index.md (güncellendi)

Toplam: 45 yeni sayfa (5 source + 5 entity + 13 concept + 22 decision). 2 ÇELİŞKİ tespit edildi (single-trip/multi-trip, öğle molası zorunluluğu) — decisions/ altında "## ÇELİŞKİ" başlığıyla işaretlendi, Stage 2'de kod satır referanslarıyla doğrulanacak.

## [2026-08-09] ingest | 2 ana Python model dosyası — CV_model_gurobi_exact.py, EV_v.1.1.py (Stage 2)

Dokunulan dosyalar (yeni):
- sources/2026-08-09-cv_model_gurobi_exact.md
- sources/2026-08-09-ev_v1_1.md
- entities/build_model_fonksiyonu.md
- entities/format_time_fonksiyonu.md
- entities/cozum_raporlama_fonksiyonlari.md
- entities/degisken_x_arc_tahsisi.md
- entities/degisken_yakit_enerji_izleme.md
- entities/parametre_big_m_100000.md
- entities/parametre_mola_zaman_sabitleri.md
- entities/degisken_route_start_route_end_ev.md
- entities/model_calistirma_parametreleri_ev.md
- decisions/karar_ev_teknisyen_cakisma_onleme_mekanizmasi.md
- decisions/karar_ev_feasibility_gurobi_tuning_ve_diagnostik.md
- decisions/karar_ev_otomatik_docx_raporlama.md
- decisions/sorun_cv_kullanilmayan_istasyon_parametreleri.md

Dokunulan dosyalar (güncellendi — Stage 1 sayfalarının Stage 2 kod okumasıyla çapraz-doğrulanması):
- decisions/celiski_single_trip_vs_multitrip.md — KRİTİK DÜZELTME: docx'ün iddia ettiği `c4_multitrip_{v}` kodda bulunamadı; hem CV hem EV kodu tek-sefer kısıtlı. Çelişki "model vs kod" değil "docx tarifi vs kodun mevcut hâli" olarak yeniden çerçevelendi. Madde silinmedi, "## ÇELİŞKİ (güncelleme)" ile ek bölüm olarak işlendi.
- decisions/celiski_ogle_molasi_zorunlulugu.md — kod satır referanslarıyla doğrulandı (CV:88-96, EV:177-183).
- decisions/sorun_sarj_yakit_istasyonlari_kodda_yok.md — CV için doğrulandı (Fc/alpha kullanılmıyor); EV için nüanslandı (S/S_set aktif, sadece klon düğüm eksik).
- decisions/sorun_kismi_sarj_dinamikleri_kodda_yok.md — EV'de kısmi şarj süresi mekanizması (`charge_time_i`) bulundu, "hiç yok" iddiası düzeltildi.
- decisions/sorun_ev_enerji_tuketim_modeli_basitlestirilmis.md — doğrusal tüketim doğrulandı, "çalışamaz durumda" ifadesi nüanslandı.
- concepts/partial_recharging.md — EV'deki `charge_time_i` mekanizması eklendi.
- entities/model_karar_degiskenleri_ve_parametreleri.md — kod-doğrulanmış değişken tablosu eklendi, status güncel.
- index.md (güncellendi)

Toplam: 15 yeni sayfa (2 source + 8 entity + 4 decision + 1 sorun), 7 mevcut sayfa güncellendi/düzeltildi. Kritik bulgu: yönerge belgesindeki bir iddia (kodda multi-trip varlığı) mevcut kodda doğrulanamadı — bu, wiki'nin "kaynaksız iddia yasak / çelişki işaretlenir, silinmez" kuralının işlediği somut bir örnek. Ayrıca EV kodunda hiçbir belgede anılmayan bir teknisyen-çakışma-önleme mekanizması bulundu.

## [2026-08-09] query | "Model↔kod farklarının tümünün genel sentezi" → filed: syntheses/model_kod_farkliliklari_genel_sentez.md

13 maddelik (2 çelişki, 5 eksiklik/sorun, 6 kod-only karar) model↔kod farkı tek bir sentez sayfasında birleştirildi: özet tablo (doğrulama durumu), kategorilere göre değerlendirme (A: gerçek çelişkiler, B: modelde olup kodda eksik, C: kodun eklediği esneklikler) ve makale öncesi önceliklendirme (6 madde, yüksek/orta/düşük öncelik). En kritik yeni gözlem: EV'nin teknisyen çakışma önleme mekanizması CV'ye portlanmamış — CV modelinde potansiyel mantık boşluğu. index.md'nin Sentezler bölümü güncellendi.

## [2026-08-09] lint | 16 bulgu (Y:3 O:8 D:5) -> Rapor: lint-report-2026-08-09.md

61 içerik sayfası (sources/entities/concepts/decisions/syntheses) + index.md/log.md tarandı. Kategori dağılımı: 1 çelişki, 2 eskimiş iddia, 3 yetim sayfa, 4 eksik kavram sayfası, 5 tek-yönlü xref (3'ü toplu), 3 zayıf-kaynak kümesi. En kritik 3 bulgu: (1) `karar_partial_charging_denklemleri_entegrasyonu_plani.md` Stage 2 bulgusuyla güncellenmemiş, güncel `sorun_kismi_sarj_dinamikleri_kodda_yok.md` ile çelişiyor; (2) `sources/2026-08-09-full_path.md` — projenin "en üst düzey" planlama belgesi, ondan türeyen 9 karar sayfasından hiçbiri geri link vermiyor; (3) "Planlanan mimari kararlar" kümesindeki 9 sayfa (hibrit algoritma mimarisi dahil) tamamen tek bir belgeye (Full Path.docx) dayanıyor, ikincil doğrulama yok. Otomatik düzeltme yapılmadı, sadece raporlandı.

## [2026-08-09] agent_architecture | 5 adet otonom ajan oluşturuldu (trsp-exact-model-mimari, trsp-hibrit-sezgisel-muhendisi, trsp-tahmin-veri-muhendisi, trsp-karsilastirma-analisti, trsp-wiki-kutuphaneci)

`raw/wshobson_agents/` referans deposundaki ajan şablon deseni (frontmatter: `name`/`description` ["Use PROACTIVELY when…" tetikleyicisi]/`model`/`tools`/`color`; gövde: Amaç/Yetkinlikler/Davranış İlkeleri/Bilgi Tabanı/Yanıt Yaklaşımı/Örnek Etkileşimler) TRSP projesine uyarlanarak `.claude/agents/` altına 5 ajan tanımlama dosyası yazıldı. Görev bölüşümü: (1) exact MIP model (Gurobi/Big-M/kısıtlar, model↔kod tutarlılığı), (2) Q-Learning+VND hibrit sezgisel tasarımı, (3) tahminleme/veri (CatBoost/TOPSIS/rolling horizon/sentetik veri), (4) exact vs heuristic karşılaştırmalı performans/Pareto analizi, (5) wiki kütüphaneci/orkestratör (INGEST/QUERY/LINT operasyonlarının yürütücüsü). Her ajanın sistem promptuna, `decisions/`+`syntheses/` klasörlerini ortak hafıza/iletişim panosu olarak kullanma zorunluluğu ve CLAUDE.md'nin hard rule'ları (raw/ salt-okunur, kaynaksız iddia yasak, sayfa silme yok, çelişkiler işaretlenir) "Kesin Sınırlar" + "İletişim Protokolü" başlıkları altında açıkça eklendi.

## [2026-08-09] skill_architecture | Ajanlar için özel yetenek dosyaları oluşturuldu ve atandı

`raw/wshobson_agents/plugins/*/skills/<n>/SKILL.md` referans şablonu (frontmatter: `name`/`description` ["Use when…" tetikleyicisi]; gövde: Genel Bakış/Ne Zaman Kullanılır/Girdi-Çıktı Formatı/Adımlar/Örnek/İlgili) TRSP'ye uyarlanarak `.claude/skills/` altına 10 atomik skill klasörü (her biri kendi `SKILL.md`'si ile) oluşturuldu: `gurobi-big-m-formulator`, `model-kod-celiski-denetleyici` (trsp-exact-model-mimari); `vnd-operator-tasarimci`, `q-learning-reward-tasarimci` (trsp-hibrit-sezgisel-muhendisi); `solomon-sentetik-veri-uretici`, `topsis-kriter-tasarimci` (trsp-tahmin-veri-muhendisi); `docx-sonuc-cikarici`, `pareto-epsilon-constraint-analiz` (trsp-karsilastirma-analisti); `obsidian-link-checker`, `wiki-sayfa-uretici` (trsp-wiki-kutuphaneci). Her skill net girdi/çıktı formatı ve adım adım süreç içeriyor. 5 ajan dosyası (`.claude/agents/*.md`) "Yetkinlikler" bölümünden hemen sonra eklenen yeni "Kullanılabilecek Yetenekler (Skills)" bölümüyle güncellendi — mevcut yapı/bağlam bozulmadan, her ajana kendi 2 skill'i atandı.

## [2026-08-10] ceo_architecture | TRSP Proje Koordinatörü ajanı sisteme eklendi

`.claude/agents/trsp-proje-koordinatoru.md` oluşturuldu — beş uzman ajanı (trsp-exact-model-mimari, trsp-hibrit-sezgisel-muhendisi, trsp-tahmin-veri-muhendisi, trsp-karsilastirma-analisti, trsp-wiki-kutuphaneci) yöneten Ana Ajan (CEO). Anayasası: kendisi içerik/kod üretmez, Eren'den gelen büyük hedefleri uzman bazında görevlere ayırır, onay almadan büyük/çok-ajanlı görev dağıtmaz. `decisions/` ve `syntheses/`'ı okuma yetkisiyle projenin güncel durumunu analiz eder; alt ajanlara iş dağıtırken `decisions/task_order_[ajan_adi]_[tarih].md` formatında Görev Emri sayfası bırakır (frontmatter `status: onay-bekliyor` → Eren onayıyla `onaylandı`). Takım artık hiyerarşik: Eren ↔ trsp-proje-koordinatoru ↔ 5 uzman ajan.

## [2026-08-10] email_dispatcher | Günlük e-posta raporlama sistemi kuruldu ve 3 alıcı tanımlandı

Kök dizine `generate_report.py` (log.md'deki bugüne ait kayıtları + `decisions/` altında bugün eklenen/güncellenen sayfaları tarayıp `daily_summary.md` üretir) ve `send_mail.py` (`daily_summary.md` içeriğini `smtplib`/`email.mime` ile SMTP üzerinden gönderir) betikleri eklendi. Alıcılar `send_mail.py` içinde sabit: melihusllu@gmail.com, hasancolak1298@gmail.com, erennbsn@gmail.com. Kimlik bilgileri koda hardcode edilmedi — `python-dotenv` ile `.env`'den (`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SENDER_NAME`) okunuyor; örnek şablon `.env.example` olarak eklendi, `.env` `.gitignore`'a alındı. `trsp-proje-koordinatoru.md`'ye "Otomatik Görev — Günlük E-Posta Raporlama" bölümü eklendi: "günlük değişiklik özetini mail olarak ilet" komutunda CEO sırasıyla `python generate_report.py` ve `python send_mail.py`'yi çalıştırıp sonucu Eren'e bildiriyor; bu işlem onay mekanizmasının "küçük/tekrarlanabilir iş" istisnasına giriyor, ayrı Görev Emri gerektirmiyor.

## [2026-08-10] email_dispatcher_onay | Mail gönderim akışına taslak-onay adımı eklendi

Eren'in isteğiyle e-posta gönderim akışı iki faza bölündü. `send_mail.py`'ye `--dry-run` bayrağı eklendi (`argparse`) — bu modda e-posta gönderilmez, gerçekte gönderilecek Kimden/Kime/Konu/Gövde birebir ekrana yazdırılır (`print_preview` fonksiyonu). `trsp-proje-koordinatoru.md`'deki "Otomatik Görev — Günlük E-Posta Raporlama" bölümü "(taslak onaylı)" olarak yeniden yazıldı: Faz 1 — `generate_report.py` + `send_mail.py --dry-run` otomatik çalışır, taslak olduğu gibi Eren'e gösterilir ve açıkça onay istenir; Faz 2 — yalnızca Eren'in açık onayından ("onaylıyorum"/"gönder"/"evet" vb.) sonra `send_mail.py` (dry-run olmadan) çalıştırılıp gerçek gönderim yapılır. Önceki "küçük iş, onay gerektirmez" istisnası bu görev için kaldırıldı — dışa (3 ekip üyesine) giden geri dönüşü zor bir iletişim olduğu için artık zorunlu onay kapılı.

## [2026-08-10] email_dispatcher_fix | .env dolduruldu, Windows konsol encoding hatası düzeltildi, sistem test edildi

`.env` dosyası oluşturuldu (SMTP_USERNAME: erenhasanmelih@gmail.com, Gmail App Password ile). İlk `--dry-run` denemesinde Windows terminalinin varsayılan kod sayfası (cp1254) `daily_summary.md` içindeki emoji karakterlerini (📋/📁) yazdıramadığı için `UnicodeEncodeError` alındı. `generate_report.py` ve `send_mail.py`'nin başına `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` eklenerek konsol çıktısı UTF-8'e zorlandı. Düzeltme sonrası `python generate_report.py` + `python send_mail.py --dry-run` uçtan uca hatasız çalıştı, taslak (Kimden/Kime/Konu/Gövde) doğru göründü — gerçek gönderim yapılmadı, sistem Eren'in onayını bekliyor.

## [2026-08-11] execution | Faz 2: Kod Düzeltmeleri (A1-A7, C1-C2) ve Wiki Güncellemesi

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
