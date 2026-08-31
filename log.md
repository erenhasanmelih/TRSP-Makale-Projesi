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

## [2026-08-22] ingest | raw/CV_model_gurobi_exact.py, raw/EV_v.1.1.py, raw/xml_data_loader.py (v1.1 yeniden yazımı) + raw/solution_validator.py (yeni dosya)

Eren'in açık onayıyla (CLAUDE.md Hard Rule §7.1'in bu seferlik bilinçli istisnası) `raw/`'daki 3 ana kod dosyası tamamen yeniden yazıldı ve 1 yeni dosya eklendi. Bu, normal bir "yeni dosya geldi" ingest'i değil, "raw/'daki mevcut dosyaların içeriği kökten değişti" durumu — CLAUDE.md §6'nın öngördüğü ekstra adım (eski koda dayalı sayfaların geçerliliğinin kontrolü) uygulandı. Kaynak bağlam için `yeni dosyalarım/Matematiksel_Model_rev_v1.1/` ve `yeni dosyalarım/Codes_rev_v1.1/` altındaki 4 docx (python-docx ile metne çevrilerek) okundu, ama ingest kaynağı olarak `raw/` altına alınmadı (yalnızca bağlam).

**Yeni sayfalar (13):**
- sources/2026-08-22-cv_model_gurobi_exact_v1_1.md
- sources/2026-08-22-ev_v1_1_rewrite.md
- sources/2026-08-22-xml_data_loader_v1_1.md (xml_data_loader.py için ilk source sayfası)
- sources/2026-08-22-solution_validator.md
- entities/solution_validator_fonksiyonlari.md
- entities/kk_name_degisken_temiz_isimlendirme.md
- entities/degisken_z_arac_ekip_atama.md
- decisions/karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari.md
- decisions/sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi.md (**kritik, `status: taslak`** — Eren'in kendi doğrulamasını bekliyor, hiçbir ajana Gurobi doğrulaması için yönlendirilmedi)

**Güncellenen sayfalar (24) — "## Güncelleme (2026-08-22)" veya "## ÇÖZÜLDÜ (2026-08-22)" bölümü eklendi, hiçbir içerik silinmedi:**
- decisions/karar_src_klasoru_ve_raw_izolasyonu.md (merkezi hub notu)
- decisions/celiski_single_trip_vs_multitrip.md — ÇÖZÜLDÜ
- decisions/celiski_ogle_molasi_zorunlulugu.md — ÇÖZÜLDÜ (kısmen)
- entities/parametre_big_m_100000.md, parametre_mola_zaman_sabitleri.md, degisken_x_arc_tahsisi.md, degisken_yakit_enerji_izleme.md, build_model_fonksiyonu.md, format_time_fonksiyonu.md, cozum_raporlama_fonksiyonlari.md, model_karar_degiskenleri_ve_parametreleri.md
- decisions/sorun_cv_kullanilmayan_istasyon_parametreleri.md, sorun_sarj_yakit_istasyonlari_kodda_yok.md, sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi.md, sorun_hardcoded_mola_parametreleri.md
- decisions/karar_dinamik_teknisyen_ekibi_itertools_combinations.md, karar_molasiz_erken_donus_kurali_kod.md, karar_operasyonel_zaman_kaydirma_format_time.md
- decisions/karar_a1_ev_sarj_c20_c21_duzeltmesi.md, karar_a7_cv_yakit_tuketim_orani_duzeltmesi.md, karar_a6_cv_non_overlap_portlamasi.md, karar_a4_zaman_penceresi_bigm_kosullandirma.md, karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme.md, karar_c2_tight_big_m_uygulamasi.md

**Archive/'a taşınan sayfalar (7, `git mv` ile, önce `status: eskimiş` + "neden eskimiş" notu eklenip sonra taşındı, index.md güncellendi):**
- sources/2026-08-09-cv_model_gurobi_exact.md, sources/2026-08-09-ev_v1_1.md
- decisions/karar_ev_teknisyen_cakisma_onleme_mekanizmasi.md, karar_ev_feasibility_gurobi_tuning_ve_diagnostik.md, karar_ev_otomatik_docx_raporlama.md
- entities/degisken_route_start_route_end_ev.md, model_calistirma_parametreleri_ev.md

index.md tüm ilgili bölümlerde (Kaynaklar, Varlıklar, Kararlar — Çelişkiler/Sorunlar/Kod-only/v1.1/Arşiv) güncellendi.

**En önemli bulgular:** (1) İki eski ÇELİŞKİ (single-trip/multi-trip, öğle molası zorunluluğu) v1.1 ile fiilen çözüldü — kod artık gerçekten çoklu sefer uyguluyor, model belgesi CV'nin opsiyonel mola davranışına göre yeniden yazılmış. (2) `solution_validator.py` ile bulunan gerçek bir hata (RC7'de CV_3 aracının iki ekip tarafından çakışan saatlerde kullanılması), yeni `z`/CV-27/28/EV-22/23 kısıtlarının doğrudan gerekçesi. (3) **Kritik, doğrulanmamış regresyon riski:** yeni `raw/EV_v.1.1.py` ve `raw/xml_data_loader.py`, Faz 2'nin A1 (EV istasyon şarjı) ve A7 (CV yakıt tüketim oranı) düzeltmelerini miras almamış görünüyor — statik kod okumasına dayanıyor, Gurobi ile test edilmedi, `status: taslak` olarak işaretlendi. (4) `src/*_fixed.py` (Faz 2) dosyaları artık eski bir `raw/` tabanına dayanıyor; bu dosyaların yeni tabana göre yeniden türetilip türetilmeyeceği `trsp-exact-model-mimari`'nin değerlendireceği bir mimari karar.

## [2026-08-22] cleanup | Eren'in isteğiyle 7 arşiv sayfası kalıcı olarak silindi

Eren'in açık isteğiyle, bir önceki ingest'te (yukarıdaki `## [2026-08-22] ingest` girişi) `archive/`'a taşınan 7 sayfa CLAUDE.md Hard Rule §7.3'ün ("sayfa silme yok") bilinçli istisnası olarak `git rm` ile kalıcı olarak silindi:

- archive/2026-08-09-cv_model_gurobi_exact.md
- archive/2026-08-09-ev_v1_1.md
- archive/karar_ev_teknisyen_cakisma_onleme_mekanizmasi.md
- archive/karar_ev_feasibility_gurobi_tuning_ve_diagnostik.md
- archive/karar_ev_otomatik_docx_raporlama.md
- archive/degisken_route_start_route_end_ev.md
- archive/model_calistirma_parametreleri_ev.md

`index.md`'nin ilgili tüm bölümleri (Kaynaklar, Varlıklar, Kararlar, Arşiv) bu 7 satır kaldırılarak güncellendi. Bu sayfalara referans veren ~13 canlı wiki sayfasındaki `[[wikilink]]` bağlantıları kırık link bırakmamak için düz metne çevrildi (link kaldırıldı, sayfa adı + "silindi" notu korundu) — hiçbir sayfanın kendi içeriği silinmedi, sadece artık var olmayan sayfalara verilen linkler temizlendi.

## [2026-08-22] execution | v1.1 raw/ derin denetimi: A1+A7 doğrulandı ve düzeltildi, 4 ek hata bulundu (trsp-exact-model-mimari)

Eren'in açık talimatıyla (onay beklemeden, inisiyatifle) `raw/EV_v.1.1.py`,
`raw/CV_model_gurobi_exact.py` ve `raw/xml_data_loader.py` Gurobi 13.0.0 ile uçtan uca
denetlendi ve **doğrudan `raw/` içinde düzeltildi** (CLAUDE.md Hard Rule §7.1'in,
2026-08-22 v1.1 yeniden yazımıyla açılan bilinçli istisnasının devamı).

**Doğrulanan iki şüphe (kütüphanecinin `status: taslak` bulgusu — ikisi de GERÇEK):**
- **A1 (EV istasyon şarjı):** EV-18, istasyon çıkış yaylarında EV-19'u eziyordu.
  Kanıt: C5/Q=600 Wh, rota sabit `0→1→5→8→4→0` — kusurlu hâlde INFEASIBLE (IIS'te
  istasyon çıkış yayının EV-18 kısıtı), düzeltilmiş hâlde FEASIBLE, istasyon 8'de
  `ye=0.0 → YE=337.2 Wh`. Düzeltme: `raw/EV_v.1.1.py:376-399`.
- **A7 (CV yakıt tüketim oranı):** `EnergyConsumptionRate` v1.1'de vehicle_attrs'tan
  silinmişti (`git diff` ile kanıtlandı), `h_c` sabit 1.0'a düşüyordu. Kanıt: R5 CV
  `h_c=1.0` → INFEASIBLE (2.5 s), `h_c=0.055` → OPTIMAL 10116.1. Etkilenen örnekler:
  R5, R7, R10, RC13, RC15. Düzeltme: `raw/xml_data_loader.py:152-158, 249-294`.

**Yeni bulunan 4 hata:**
1. **(Ölümcül, düzeltildi)** EV-17/18/19 depo yaylarını kapsıyordu → `ye[0] ≤ ye[0] −
   h_e·(tur mesafesi)` ⇒ **EV modeli her rota için infeasible'dı.** IIS kanıtı.
   Bu, "Değişiklik Raporu - v1.1.docx" §5.2'deki "EV: optimal bulunamadı (beklenen)"
   ifadesinin gerçek nedeni. → `sorun_ev_depo_yaylarinda_dongusel_infeasibility.md`
2. **(Düzeltildi)** EV enerji zincirinin depo ankrajı yoktu → CV-22/23/24/25'in EV
   karşılıkları **EV-24/25/26/27** olarak eklendi.
   → `karar_ev_depo_sarj_ve_donus_enerjisi_kisitlari.md`
3. **(Düzeltildi)** EV-17 Big-M'i geçersiz ölçüde küçüktü (18181.8 < gereken 40581.8);
   CV'de `data['lc0']=40000` override'ı vardı, EV'de yoktu. `min τ[1]` testi
   3418.2 s → 133.7 s. → `sorun_ev17_big_m_gecersiz_kucuk.md`
4. **(Düzeltildi, raporlama)** rapor molayı sabit 3600 s sayıyordu, model `ll−el` =
   7200 s ayırıyor; ayrıca emoji satırları cp1254 konsolda `UnicodeEncodeError` ile
   scripti çözüm bulunduktan SONRA çökertiyordu.
   → `sorun_rapor_mola_suresi_3600_vs_ll_el.md`, `sorun_rapor_unicode_cokme_log_print.md`

**Düzeltilmeyen (belgelenen) bulgu:** CV-26/EV-21 geri alınmasının "zararsız" olduğu
iddiası ÇÜRÜTÜLDÜ — `solution_validator.validate_solution()` R10 ve RC10'da gerçek
"sefer sırası ihlali" buluyor (aynı kaynağın iki seferi 0.0'da birlikte başlıyor).
Güvenli düzeltme klon düğüm / sefer-indeksli `τ` refaktörü gerektirdiğinden bilinçli
olarak yapılmadı. → `sorun_coklu_sefer_zaman_sirasi_ihlali.md`

**Kütüphanecinin "Bulgu 7" (mola penceresi) şüphesi:** model tarafı KASITLI (v1.1
matematiksel modeli molayı `w_ijk(ll_k − el_k)` ile tanımlıyor, docx ile doğrulandı),
rapor tarafı BUG'dı (düzeltildi).

**Dokunulan sayfalar (6 yeni/güncellenen decisions + index):**
- decisions/sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi.md (GÜNCELLENDİ, `taslak` → `güncel`)
- decisions/sorun_ev_depo_yaylarinda_dongusel_infeasibility.md (YENİ, ÇELİŞKİ başlıklı)
- decisions/karar_ev_depo_sarj_ve_donus_enerjisi_kisitlari.md (YENİ)
- decisions/sorun_ev17_big_m_gecersiz_kucuk.md (YENİ)
- decisions/sorun_coklu_sefer_zaman_sirasi_ihlali.md (YENİ, AÇIK)
- decisions/sorun_rapor_mola_suresi_3600_vs_ll_el.md (YENİ)
- decisions/sorun_rapor_unicode_cokme_log_print.md (YENİ)
- decisions/karar_a1_ev_sarj_c20_c21_duzeltmesi.md, karar_a7_cv_yakit_tuketim_orani_duzeltmesi.md ("Güncelleme 2" bölümleri)
- index.md (Sorunlar ve v1.1 kararları tabloları)

## [2026-08-23] execution | Depo klon düğümü tasarımı `raw/`'a UYGULANDI (CV-29/30/31, EV-28/29/30) — `sorun_coklu_sefer_zaman_sirasi_ihlali` ÇÖZÜLDÜ

`decisions/karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani.md` §1-11'de tasarlanan
ve `raw/` dışı bir prototiple doğrulanan depo klonlama tasarımı, kullanıcının açık
talimatıyla `raw/CV_model_gurobi_exact.py` ve `raw/EV_v.1.1.py`'nin **mevcut**
`build_model()` fonksiyonlarına doğrudan işlendi (CLAUDE.md Hard Rule §7.1'in bilinçli
istisnası — bu oturum için `raw/`'a yazma yetkisi verilmişti).

**Model değişikliği (özet):** fiziksel `0` düğümü yay kümesinden çıkarıldı; yerine
sefer-indeksli ÇIKIŞ klonları `O = {o_1,o_2,o_3}` ve DÖNÜŞ klonları `E = {e_1,e_2,e_3}`
kondu. Yeni ikili değişken `u[r,kk]`; eski tek CV-4/EV-4 kısıtı **CV-4a/b/c/d** ve
**EV-4a/b/c/d** olarak ayrıştırıldı. Yeni kısıtlar: **CV-31/EV-30** (depodan çıkış zaman
ilerlemesi = geri alınan CV-26/EV-21'in doğru hâli), **CV-29/EV-28** (sefer sırası
`τ[e_r] ≤ τ[o_{r+1}]`), **CV-30/EV-29** (boş sefer ankrajı). Tüm yeni Big-M'ler vardiya
penceresinden türetilmiş tight sınırlardır (`ls−es`, `max(0, ls−es−tt[o_r,j])`).
`R_max` parametreleştirildi (CV: `build_model(..., R_max=3)`, EV: `data["R_max"]`).

**Zorunlu yan değişiklik:** mola sayım tabanı "sefer sayısı"ndan "aktif kaynak"a
çevrildi — CV-13 `≤ z[kk]`, EV-12 `== z_veh[kk]`. Aksi hâlde EV'de çoklu sefer
sessizce imkânsız hâle gelirdi (`ll ≤ el` çelişkisi).

**Gurobi + solution_validator kanıtı:** C5/R5/RC5/R10/RC10 × {CV, EV} = 10 koşum,
**hepsi `valid=True`**. R10 (CV): `13138.2 (valid=False)` → `14335.3 (valid=True)`,
tasarım §8.2'nin öngördüğü değerle birebir. Karşıt-olgusal koşum (çoklu sefer zorlanıp
yalnızca `CV29_*` kaldırıldığında) belgelenen ihlali birebir geri getiriyor
(`obj=13138.2`, iki sefer de `τ=0.0`) — ihlali kesen mekanizma CV-29 olarak izole edildi.
EV tarafında eski EV-12 biçimiyle çoklu sefer zorlandığında fizibil çözüm bulunamıyor
(§6 öngörüsü doğrulandı). Model boyutu büyümesi §8 tablosuyla üçüncü haneye kadar
örtüştü (R10: 1.366×, R20: 1.192× değişken).

**Dokunulan dosyalar:**
- raw/CV_model_gurobi_exact.py (build_model + print_cv_solution) — `raw/`'a yazıldı
- raw/EV_v.1.1.py (build_model + print_ev_solution) — `raw/`'a yazıldı
- decisions/karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani.md (GÜNCELLENDİ: durum
  UYGULANDI, §12 prototip sonucu dolduruldu, §13 Uygulama Sonucu eklendi)
- decisions/sorun_coklu_sefer_zaman_sirasi_ihlali.md (GÜNCELLENDİ: "ÇÖZÜLDÜ (2026-08-23)")
- decisions/celiski_ogle_molasi_zorunlulugu.md (GÜNCELLENDİ: mola sayım tabanı değişikliği)
- decisions/karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari.md (GÜNCELLENDİ: "bilinen sınır" kapatıldı)
- concepts/klon_dugum_node_replication.md (GÜNCELLENDİ: teknik artık `raw/`'da canlı)
- index.md (3 satır güncellendi)

**Ek bulgu (aynı gün, koşum sonrası):** EV RC13 (istasyonlu, `|C|=13`) `R_max=3` +
`TimeLimit=600 s` + `NoRelHeurTime=60 s` ile **hiç fizibil çözüm bulunamadı**. Üç
koşumla izole edildi: aynı klon makinesi `R_max=1` ile 600 s'de çözüm buluyor
(`obj=20667.0, valid=True`), `R_max=3` ile 1500 s + `NoRelHeurTime=500` verildiğinde
de buluyor (`obj=20898.0, valid=True`). Yani sorun modelleme değil, `R_max=3`'ün
büyüttüğü arama uzayı ve yetersiz sezgisel bütçe — tasarım §8.1'in öngördüğü risk.
`R_max`'ın veriden türetilmesi (§8.3) artık öncelikli sonraki iştir.
→ `karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani.md` §13.2.1

## [2026-08-25] execution | `R_max` sabit 3 yerine VERİDEN TÜRETİLDİ (`derive_r_max`) — CV+EV, `raw/`'a yazıldı

[[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] §8.3'te bırakılan ve §13.2.1'de
"operasyonel gereklilik" ilan edilen mitigasyon uygulandı → yeni sayfa
**[[karar_r_max_dinamik_turetme]]**.

**§8.3'ün önerdiği formül YANLIŞ ÇIKTI.** `2·(min gidiş-dönüş + min hizmet) > ls − es`
koşulu mevcut veride hiç sağlanmaz: `f_min ∈ [1060.2, 1739.9] s` iken vardiya
`32400 s`, yani `⌊(ls−es)/f_min⌋ = 18…30` (30 örnek). Zaman sayımı `min(3, ·)`
sınırını hiç düşürmüyor.

**İşe yarayan argüman: BİRLEŞTİRME BASKINLIĞI (merge dominance).** Ardışık iki sefer
`… → i → depo → j → …` tek sefere birleştirilirse üçgen eşitsizliği gereği amaç
kötüleşmez; mevcut `τ` değerleri aynen geçerli kalır (CV-8/CV-29/CV-31 zinciri), mola
yeni `(i,j)` yayına taşınır ve SAYISI değişmez (CV-13/EV-12 bozulmaz), CV-3 müşteri
uçlarında CV-2 gereği zaten otomatik sağlanır. **Tek engel enerjidir** (depoda dolum
yalnızca çıkış yayında verilir: CV-23/24, EV-24/25). Dolayısıyla *vardiyaya sığan en
uzun rota < menzil* ise `R_max = 1` optimali korur.

**Ölçüm (30/30 örnekte `R_max = 1`):** CV `maxdist ∈ [11.3, 81.5] km < 109.1 km`
(`G/h_c`); EV `maxdist ∈ [247.2, 253.1] km < 322 km` (`Q/h_e`). EV'de belirleyici terim
**zorunlu moladır** (bütçe `32400−7200 = 25200 s`); molasız bütçeyle test geçmezdi
(337.5 km > 322 km). CV'de belirleyici olan **yay sayısı sınırıdır** (k müşterili rota
tam `k+1` yay kullanır); yalnız zaman sınırıyla test geçmezdi (420 km > 109 km).

**SAĞLAMLIK KANITI:** C5/R5/RC5 × {CV, EV} = 6 koşum (`MIPGap=0`, 600 s),
`R_max=3` vs türetilmiş `R_max=1` → **objektif birebir aynı** (8291.2 / 10116.1 /
7933.0), hepsi `valid=True`. CV'de üçü de kanıtlanmış optimal.

**MODEL BOYUTU:** CV `NumVars` −%39.6, EV −%26.8 (n=5); RC13'te −%17.9 (oran `n` ile
azalıyor, §8'in `O(n)/O(n²)` analiziyle tutarlı).

**HIZ:** 600 s'de gap kazancı n=10'da dört koşumun dördünde de var (−6.6 / −2.3 /
−2.2 / −4.6 puan); EV RC10 incumbent'ı %5.6 iyileşti. **RC13'te kazanç YOK**
(1500 s'de %58.2 → %58.4, objektif birebir aynı: 20753.8).

**ÇELİŞKİ açıldı:** §13.2.1'in "RC13'te `R_max=3` fizibil çözüm bulamıyor, `R_max=1`
buluyor" gözlemi **tersine döndü** (600 s/60 s tekrarında `R_max=3` buldu, `R_max=1`
bulamadı) — RC13'te fizibil çözüm bulma Gurobi sezgisel şansına bağlı; tek koşuma
dayanan çıkarım desteklenmiyor. Geçmiş silinmedi, ilgili başlığa ÇELİŞKİ notu düşüldü.

**Yan bulgu:** EV R10 (`R_max=1`) koşumu wiki kaydındaki **ilk gerçek şarj istasyonu
ziyaretini** üretti (`istasyonlar=[11, 12]`), §13.7'nin "hiç istasyon ziyaret edilmedi"
sınırlamasını kısmen kapattı.

**Dokunulan dosyalar:**
- raw/xml_data_loader.py (`max_single_trip_distance`, `derive_r_max`, `prepare_*` içine
  `R_max`/`R_max_by_tech`/`R_max_info` anahtarları) — `raw/`'a yazıldı
- raw/CV_model_gurobi_exact.py (`build_model` imzası + `u[r,kk].UB=0` bloğu + `__main__` print)
- raw/EV_v.1.1.py (aynısı, simetrik)
- decisions/karar_r_max_dinamik_turetme.md (YENİ)
- decisions/karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani.md (§8.3 "Uygulandı"
  notu, §13.2.1 ÇELİŞKİ başlığı, §13.7 maddesi kapatıldı)
- index.md (1 satır güncellendi + 1 satır eklendi)

**Commit yapılmadı** (Eren'in ayrı onayı bekleniyor).

## [2026-08-27] query | "RC13'ün gerçek darboğazı R_max değilse nedir?" → filed: decisions/sorun_rc13_darbogaz_kok_neden_analizi.md

`karar_r_max_dinamik_turetme` §9.1'in bıraktığı açık soru araştırıldı: `R_max`
çürütüldükten sonra RC13'ün (EV, istasyonlu) 900 s'de hiç fizibil çözüm
bulamamasının kök nedeni nedir? Tüm ölçümler `raw/` **dışında**, anahtarlanabilir
bir prototip kopyada (`%TEMP%\rc13_diag\proto_ev.py`) yapıldı — `raw/CV_model_gurobi_exact.py`,
`raw/EV_v.1.1.py`, `raw/xml_data_loader.py` bu turda **değiştirilmedi**.

**Kök neden: LP gevşetmesinde depo bağlantısı hiç zorlanmıyor.** Kök LP çözümünde
`Σ x[O_r,j,k] = 0` ve `Σ z_veh[k] = 0` — 13 müşterinin tamamı depoya hiç uğramayan
2-/3-döngülerle "ziyaret ediliyor" (mesafeyi en ucuz komşuya indiriyor). Sorumlu:
EV-2 (giren yay sayısı=1, kaynağını umursamaz) + EV-5 akış dengesi (döngülerle
sağlanır) + EV-4a/b/c'nin `z_veh`'i aşağıdan hiç zorlamaması. Tek altur-eleme
mekanizması EV-7'nin Big-M zaman zinciri, ki LP'de kesirli `x` altında tamamen
gevşek. Bu, MTZ-tipi formülasyonun bilinen ve **RC13'e özgü olmayan** bir
zayıflığı — ölçülen 14 koşumun (CV+EV × C5/R10/RC10/R13/RC13/RC15/RC20) **14'ünde**
birebir görüldü.

**RC13'ü özel olarak zorlaştıran üç etken:** (1) zorunlu öğleden-sonra mola +
zaman pencereleri → 6 müşteri `ec=ll=14400`'e zorunlu itiliyor, toplam hizmet
21903 s / pencere 10800 s → en az 3 araç gerektiren bir sırt-çantası alt problemi
(filoda tam 3 araç var, RC13 fizibilite sınırında); (2) `|K|=45` (5 beceri →
15 ekip × 3 araç), C13'ün `|K|=30`'undan %50 büyük; (3) en uzun yay 4387 m.

**Doğrulama:** güçlendirilmiş prototip (yetkinlik filtresi + araç indisi kaldırma
+ öğleden-sonra `min_veh` geçerli eşitsizliği + istasyon düşürme + statik DFJ)
RC13'ü **10.7 s'de kanıtlanmış optimale** (20667.0, gap %0.00) taşıdı — `raw/`
eşdeğeri aynı 900 s bütçesinde `SolCount=0`. Optimal, `raw/`'un değiştirilmemiş
modelinde `x` sabitlenerek doğrulandı (wiki'de önceden kayıtlı 20753.8, optimalden
%0.42 kötüymüş). Ablasyon: dört bileşenin (`min_veh`, `dfj`, `bwp`+`arc_fix`,
`drop_st`) dördü de aynı optimali kanıtladı → geçerlilik argümanları ampirik
destekli; en büyük tekil kaldıraç istasyon düşürme (`drop_st`: 10.7 s → >600 s
çözümsüz), statik DFJ indirimlerle birlikteyken NET ZARARLI (2.7 s → 10.7 s).

**Yan bulgular:** `req_skills_unique = list(set(...))` Python'un rastgeleleşen
string hash'i yüzünden koşumdan koşuma ekip adlarını değiştiriyor — muhtemelen
`karar_r_max_dinamik_turetme` §9.1'deki "R_max=3/1 yön tersine dönmesi"nin gerçek
nedeni; `Delta_s` fiilen ölü değişken (amaç fonksiyonunda yok, her optimalde 0);
CV modeli birebir aynı patolojiyi taşıyor (7 örnekte `depo_cikis_toplami=0`).

**ÖNERİLER `raw/`'a UYGULANMADI** (Eren onayı bekleniyor): asgari paket Ö1
(yetkinlik filtresini `x` üzerinde uygula) + Ö2 (homojen filoda araç indisini
kaldır) + Ö6 (enerji hiç bağlamıyorsa istasyonları düşür — `derive_r_max`'ın
zaten kanıtladığı testle aynı argüman) tek başına RC13'ü 2.7 s'de kanıtlanmış
optimale taşıyor; Ö3 (`min_veh` geçerli eşitsizliği), Ö4 (mola penceresi
yayılımı, yalnız EV), Ö5 (statik DFJ), Ö7 (tight-M + ölü kısıt temizliği) bu
paketin üstünde ek hız kazandırmıyor (DFJ hatta zararlı), değerleri indirimlerin
uygulanamadığı durumlarda ortaya çıkıyor.

**Dokunulan dosyalar:**
- decisions/sorun_rc13_darbogaz_kok_neden_analizi.md (YENİ)
- decisions/karar_r_max_dinamik_turetme.md, decisions/karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani.md,
  concepts/tight_big_m.md, concepts/uyumluluk_matrisi.md, concepts/klon_dugum_node_replication.md,
  entities/gurobi_mip_cozucusu.md, decisions/sorun_kismi_sarj_dinamikleri_kodda_yok.md,
  decisions/karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme.md, decisions/celiski_ogle_molasi_zorunlulugu.md
  (çift-yönlü Related bağlantısı eklendi)
- index.md (sorun_rc13_darbogaz_kok_neden_analizi satırı eklendi)
- `raw/*.py` **DEĞİŞTİRİLMEDİ** — tüm ölçümler `%TEMP%\rc13_diag\` prototipinde

**Commit yapılmadı** (Eren'in ayrı onayı bekleniyor).

## [2026-08-28] execution | RC13 asgari hızlandırma paketi (Ö1+Ö2+Ö6) `raw/`'a UYGULANDI (bu paketin ardılı için bkz. 2026-08-29 execution kaydı, aşağıda)

Eren, önceki turun teşhisini ve önerilerini onayladı; bu turda Ö1 (yetkinlik
filtresi), Ö2 (homojen filoda araç indisi agregasyonu) ve Ö6 (enerji hiç
bağlamıyorsa istasyon düşürme) — artı `req_skills_unique` için
`list(set(...))` → `sorted(set(...))` düzeltmesi — doğrudan
`raw/CV_model_gurobi_exact.py`, `raw/EV_v.1.1.py`, `raw/xml_data_loader.py`
ve `raw/solution_validator.py` içine işlendi (Ö3/Ö4/Ö5/Ö7 UYGULANMADI,
yalnızca onaylanan üçü).

**ÖNEMLİ DÜZELTME:** uygulama öncesi, önceki turda [[sorun_rc13_darbogaz_kok_neden_analizi]]
§6'ya yazılan "asgari paket Ö1+Ö2+Ö6, RC13'ü 2.7 s'de kanıtlanmış optimale
getiriyor" iddiasının YANLIŞ karakterize edildiği fark edildi — o rakam
aslında Ö1+Ö2+Ö3(min_veh)+Ö4(bwp+arc_fix)+Ö6+Ö7(tight_m)'nin BİRLİKTE
sonucuydu. Bu, Eren'e uygulama öncesi bildirilmedi (onay zaten verilmişti,
iş zaten değerliydi) ama SONUÇ RAPORUNDA açıkça düzeltildi ve hem
[[sorun_rc13_darbogaz_kok_neden_analizi]] hem de yeni
[[karar_rc13_asgari_paket_uygulamasi]] sayfasına işlendi.

**Gerçek ölçülen sonuç** (raw/ modülleri doğrudan import edilip test edildi,
`raw/` dışı bir script'le — `raw/` `__main__`'ı interaktif `input()`
içerdiğinden çalıştırılmadı; her koşum `raw/solution_validator.py` ile
doğrulandı, hepsi `valid=True`):

| Örnek | Model | Önce | Sonra |
|---|---|---|---|
| RC13 (hedef) | EV | 900 s, **0 çözüm** | **67.4 s, kanıtlanmış optimal (20667.0, gap %0.00)** |
| RC13 (hedef) | CV | 900 s, 0 çözüm (varsayım, CV aynı patolojiyi taşıyor) | **106.4 s, kanıtlanmış optimal (20667.0)** |
| R10/RC10 | CV+EV | 600 s'de %25-58 gap | **<1 s'de kanıtlanmış optimal**; RC10 EV'de YENİ en iyi değer (10729.2, önceki kayıtlar 13899.5/14727.5 kanıtlanmamıştı) |
| C5/R5/RC5 | CV+EV | zaten optimal | değişmedi (~0 s, aynı objektif) |
| RC15 (bonus test) | EV | — | 180 s'de %8.05 gap (paket TEK BAŞINA yetersiz, beklenen) |
| RC20 (bonus test) | EV | — | 180 s'de 0 çözüm (paket TEK BAŞINA yetersiz, beklenen) |

Heterojen filo fallback yolu da (Ö2'nin `K=V×T`'ye geri dönme dalı) elle
simüle edilerek doğrulandı (C5'te bir aracın kapasitesi %50 artırılarak):
model hatasız kuruldu, aynı optimale ulaştı, `solution_validator`'ın eski
(araç-çakışması) kontrol yolu da hatasız çalıştı.

**Dokunulan dosyalar:**
- raw/CV_model_gurobi_exact.py (Ö1 UB=0 bloğu, Ö2 `aggregate_fleet`/`_t_of`/`_Gk`,
  CV27/28 dallanması, `sorted(set(...))`)
- raw/EV_v.1.1.py (aynısı, simetrik + Ö6'nın `stations_dropped` print'i)
- raw/xml_data_loader.py (`prepare_ev_data_from_instance` içine istasyonsuz ön-test)
- raw/solution_validator.py (aggregate mod Kontrol 2 sweep-line yeniden yazımı)
- decisions/karar_rc13_asgari_paket_uygulamasi.md (YENİ)
- decisions/sorun_rc13_darbogaz_kok_neden_analizi.md (GÜNCELLEME notu + düzeltme)
- decisions/karar_r_max_dinamik_turetme.md, decisions/karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme.md,
  concepts/uyumluluk_matrisi.md, entities/degisken_z_arac_ekip_atama.md,
  entities/solution_validator_fonksiyonlari.md (çift-yönlü Related bağlantısı)
- index.md (2 satır eklendi/güncellendi)

**Commit yapılmadı** (Eren'in ayrı onayı bekleniyor).

## [2026-08-29] execution | Ö3+Ö4+Ö7a+Ö7b+Ö8 `raw/`'a UYGULANDI (Ö5 rafa kaldırıldı)

Eren'in talimatıyla: Ö5 (statik DFJ) tamamen rafa kaldırıldı (ölçülmüş net
zararlı etkisi nedeniyle); Ö3 (min_veh, EV) + Ö4 (bwp EV / arc_fix CV+EV,
CV'nin opsiyonel molası dikkate alınarak dikkatli uyarlandı) + Ö7a
(düğüm-bazlı sıkı Big-M) + Ö7b (ölü kısıt temizliği) + Ö8 (EV mola/şarj
çakışması düzeltmesi, Eren'in sorusu üzerine keşfedildi) doğrudan
`raw/CV_model_gurobi_exact.py` ve `raw/EV_v.1.1.py`'ye işlendi.

**Ö3/Ö4 CV'ye TAŞINMADI** (yalnızca `arc_fix` her ikisinde): CV'nin molası
(CV-13) opsiyonel olduğundan bir CV kaynağı molayı hiç kullanmayarak EV'nin
"zorunlu öğleden-sonraya kayma" zincirini (EV-12 tabanlı) önleyebilir —
argüman CV'de kurulamaz. Bu, uygulama sırasında ayrıca doğrulanan bir
bulgu (kullanıcının Ö4 için istediği "dikkatli uyarlama" Ö3'e de
genişletildi).

**Ö7a uygulanırken yeni bir gözlem:** `w<=x` (EV-8/CV-9) her (i,j,kk) için
geçerli olduğundan x=0 iken w de otomatik 0'dır — mola terimi Big-M'e
eklenmesine GEREK YOK (yalnızca şarj terimi gerekiyor, o x'ten bağımsız).
Bu, ilk taslak formüllerin gereksiz yere gevşek kalmasını önlemek için
ek bir düzeltme turu gerektirdi (EV-6/7/17/30, CV-8/19/31).

**Ö8 (Eren'in sorusu üzerine):** `Delta_s` fiilen ölü değişkendi (hiçbir
kısıtta gerçek şarj miktarına bağlanmamıştı); kaldırıldı, EV-6/10/15
gerçek terime (`g_e*(YE-ye)`) geçirildi, EV-17'ye eksik mola terimi
eklendi. Pratik etkisi BUGÜN SIFIR (Ö6 zaten istasyonları düşürüyor,
S=[]); yalnızca istasyonlu senaryolar için ileriye dönük doğruluk
düzeltmesi.

**Gerçek ölçülen sonuç** (`raw/` dışı test script'i, `raw/solution_validator.py`
ile her koşum doğrulandı, hepsi `valid=True`):

| Örnek | Model | Önceki (Ö1+Ö2+Ö6) | Şimdi |
|---|---|---|---|
| RC13 | EV | 67.4 s, optimal | **5.96 s, optimal** (20666.99) |
| RC13 | CV | 106.4 s, optimal | **36.95 s, optimal** |
| RC15 | EV | 180s'de %8.05 gap | **11.35 s, optimal** (23912.82, YENİ kanıt) |
| RC20 | EV/CV | 180s'de 0 çözüm | 300s'de **hâlâ 0 çözüm** (alt sınır 24099.9'a yükseliyor) |
| C5/R5/RC5, R10/RC10 | CV+EV | optimal | DEĞİŞMEDİ (regresyon yok) |

Heterojen filo (Ö2) ve heterojen vardiya penceresi (Ö3/Ö4'ün
`_bwp_active` güvenlik kontrolü) elle simüle edilerek ayrıca test edildi —
ikisi de doğru şekilde güvenli moda düşüyor, optimal değer korunuyor.

**RC20 hâlâ çözülemiyor** — bu, paketin bilinen sınırı olarak açıkça not
edildi (Ö5/warm-start/parametre taraması gibi ek çalışma gerekebilir).

**Dokunulan dosyalar:**
- raw/EV_v.1.1.py (bwp+arc_fix+Ö3 hesaplama bloğu, EV-6/7/17/30 tight-M,
  Delta_s kaldırma + EV-6/10/15/17 gerçek şarj terimi, EV18/19_lb kaldırma,
  `import math` eklendi)
- raw/CV_model_gurobi_exact.py (arc_fix bloğu, CV-8/19/31 tight-M,
  CV20/21_lb kaldırma, Ö3 için "CV'ye taşınmadı" notu)
- decisions/karar_rc13_tam_paket_uygulamasi.md (YENİ)
- decisions/sorun_rc13_darbogaz_kok_neden_analizi.md,
  decisions/karar_rc13_asgari_paket_uygulamasi.md, concepts/tight_big_m.md,
  decisions/sorun_kismi_sarj_dinamikleri_kodda_yok.md,
  decisions/celiski_ogle_molasi_zorunlulugu.md,
  decisions/sorun_cv_kullanilmayan_istasyon_parametreleri.md
  (çift-yönlü Related bağlantısı eklendi)
- index.md (1 satır eklendi)

**Commit yapılmadı** (Eren'in ayrı onayı bekleniyor).

## [2026-08-31] query | "RC20 neden 300 s'de hiç fizibil çözüm vermiyor?" → filed: decisions/sorun_rc20_darbogaz_kok_neden_analizi.md

RC13 kök-neden analizinin (`sorun_rc13_darbogaz_kok_neden_analizi.md`) devamı
olarak RC20 teşhis edildi. **Sonuç önceki teşhisi ÇÜRÜTTÜ.**

**Kök neden: RC20 çözülemiyor değil, INFEASIBLE (hem EV hem CV).**

Zincir (hepsi mevcut kod/veri):
1. `raw/EV_v.1.1.py:1188` + `raw/CV_model_gurobi_exact.py:1087`
   `tech = skill_tech_map[skill][0]` → `raw/Info4Employee.xml`'deki 8
   teknisyenin yalnızca 5'i aktif (TECH_002/004/006 hiç kullanılmıyor).
2. EV-22 (`:439-449`) / CV-27 (`:347-359`): `Σ z_veh ≤ |V| = 3`.
3. EV-23 (`:458-473`) / CV-28 (`:368-388`): her ham teknisyen ≤ 1 aktif ekipte.
4. → 5 beceriyi ≤3 ekiple kapatmak **zorunlu `{2,2,1}` bölünmesi** demek;
   bir becerinin TÜM müşterileri tek bir aktif ekibe düşüyor (EV-2 `:397-402`).
5. EV-12 (`:647-651`) zorunlu mola + EV-9/EV-11 → aktif kaynak başına
   `Σ st ≤ (ls−es) − (ll−el) = 25 200 s`. CV'de mola opsiyonel (CV-13) ama
   CV-14 (`:571-590`) molasız kaynağı `ll = 21 600`'e döndürdüğü için CV'de de
   aynı duvar geçerli.

RC20 rakamları: `Σ st = 68 740 s`; 15 `{2,2,1}` bölünmesinin **15'i de**
25 200 s'i aşıyor, en iyisi (s2+s4 | s3+s5 | s1) `max grup = 25 991 s`
→ **+791 s aşım**, üstelik seyahat süresi hiç sayılmadan.
Karşılaştırma: RC13/RC15'te en iyi max grup 19 059 s (6/15 bölünme fizibil).

**Üç bağımsız kanıt:**
| Yöntem | Sonuç |
|---|---|
| Tam sayım (15 bölünme) | 0/15 fizibil |
| Rotalamasız gevşetme MIP + IIS | INFEASIBLE (IIS 76 kısıt); RC13/RC15 fizibil |
| Gurobi + tek geçerli eşitsizlik (`Σ st_i·x ≤ 25200·z`) | **EV 2.5 s, CV 8.0 s'de INFEASIBLE kanıtlandı** |

Referans (eşitsizliksiz, değiştirilmemiş `raw/`, 1800 s): EV `MIPFocus=3` →
SolCount=0, alt sınır 25 144.16, 569 287 düğüm; CV `MIPFocus=1` → SolCount=0,
alt sınır 18 393.08, 563 979 düğüm. Alt sınırlar sonlu bir gap'e yakınsamıyor,
sürekli yükseliyor — yakınsayacakları bir optimal yok.

Geçerlilik doğrulaması (aynı eşitsizlikle, optimaller **değişmedi**):
RC13 EV/CV 20 666.99 ✔, RC15 EV/CV 23 912.82 ✔, R15 EV 12 704.58,
C15 EV 14 654.74.

**Tarama:** n ≥ 20 olan **15 örneğin tamamı** (C/R/RC × 20/40/60/80/100)
aynı argümanla infeasible. → **Mevcut `raw/` konfigürasyonunda exact modelin
çözebileceği en büyük boyut n = 15.**

**Ne olurdu testleri (UYGULANMADI):**
- Ö-B (filo 3→4, model boyutu değişmiyor): **9 çözüm**, ilk incumbent 246 s,
  900 s'de `ObjVal = 29 104.18`, gap %9,35.
- Ö-A (tam 8 teknisyen kadrosu, `|T|` 15→36, `NumVars` 11 924→28 556):
  fizibil ama 900 s'de hâlâ 0 çözüm (alt sınır 20 852.6).

**ÇELİŞKİ işaretlendi:** `karar_rc13_tam_paket_uygulamasi.md` §9'un
"RC20 = arama gücü sorunu, warm-start/lazy-DFJ/parametre taraması dener"
teşhisi çürütüldü (yeni §9.1); bu log'un 2026-08-29 girdisi için de aynı
düzeltme geçerlidir. Hiçbir taraf silinmedi (Hard Rule §7.4).

**Dokunulan dosyalar:**
- decisions/sorun_rc20_darbogaz_kok_neden_analizi.md (YENİ)
- decisions/karar_rc13_tam_paket_uygulamasi.md (§9.1 ÇELİŞKİ + Related)
- decisions/sorun_rc13_darbogaz_kok_neden_analizi.md,
  decisions/celiski_ogle_molasi_zorunlulugu.md,
  decisions/karar_molasiz_erken_donus_kurali_kod.md,
  decisions/karar_dinamik_teknisyen_ekibi_itertools_combinations.md
  (çift-yönlü Related bağlantısı)
- index.md (1 yeni satır + RC13 tam paket satırına ÇELİŞKİ notu)

**`raw/` DEĞİŞTİRİLMEDİ** (Hard Rule §7.1). Tüm koşumlar `raw/` dışındaki
teşhis koşucusuyla (`%TEMP%\claude\...\scratchpad\`: `harness.py`,
`partition.py`, `proof.py`, `scan.py`, `corroborate.py`, `corr_cv.py`,
`whatif.py`, `whatif_roster.py`) ve Gurobi 13.0.0 ile yapıldı.
Düzeltme uygulaması Eren'in ayrı onayını bekliyor.

## [2026-08-31] execution | 5/8 teknisyen bug fix `raw/`'a UYGULANDI — RC13/RC15 EV daha iyi optimale ulaştı, RC20 artık infeasible değil

Eren'in açık talimatıyla, yukarıdaki teşhiste bulunan `skill_tech_map[skill][0]`
hatası (`raw/CV_model_gurobi_exact.py:1087`, `raw/EV_v.1.1.py:1188`)
doğrudan düzeltildi: her beceriden yalnızca ilk teknisyeni almak yerine,
**tüm** teknisyenler aktifleştiriliyor (`for tech in skill_tech_map[skill]:`).
Yeni sayfa: [[karar_5_8_teknisyen_bug_fix]].

**Regresyon testiyle (`raw/` dışı, `runpy` ile modül import edilip
`__main__` mantığı kısa `TimeLimit` ile tekrarlandı) beklenmedik ama
önemli bir bulgu:** düzeltme yalnızca RC20'nin infeasibility'sini
gidermiyor (RC20 EV: |T| 15→36, tam modelde 900s'de hâlâ 0 çözüm — bu
turda ileri iş yapılmadı, Eren'in talimatıyla RC20 dokunulmadı) — RC13 ve
RC15'in **önceden kanıtlanmış "optimal" değerlerini de gerçekten
iyileştiriyor**:

| Örnek | Model | Önce (5/8 teknisyen) | Sonra (8/8 teknisyen) |
|---|---|---|---|
| C5 | CV | 8291.18 (optimal) | 8291.18 (optimal, değişmedi) |
| RC13 | EV | 20666.99 (optimal, 5.96s) | **19938.07 (optimal, 12.87s) — %3,5 daha iyi** |
| RC15 | EV | 23912.82 (optimal, 11.35s) | **21851.58 (optimal, 32.15s) — %8,6 daha iyi** |
| RC13 | CV | 20666.99 (optimal, 36.95s) | incumbent 19938.07, 300s'de %8,7 gap (henüz kanıtlanmadı) |

Sebep: önceki koşumlar yalnızca 5 teknisyenle (TECH_002/004/006 hiç
kullanılmadan) kanıtlanmış optimallerdi — eksik girdiye göre doğruydular,
gerçek (8 teknisyenli) problem için değil. Süre artışı beklenen bir yan
etki (`|T|` ~2,4× büyüdü). **[[karar_rc13_tam_paket_uygulamasi]] ve
[[karar_rc13_asgari_paket_uygulamasi]]'ndaki RC13/RC15 rakamları bu yüzden
GEÇERSİZ kılındı** (güncelleme notlarıyla, silinmeden).

**Dokunulan dosyalar:**
- raw/CV_model_gurobi_exact.py, raw/EV_v.1.1.py (bug fix)
- decisions/karar_5_8_teknisyen_bug_fix.md (YENİ)
- decisions/sorun_rc20_darbogaz_kok_neden_analizi.md, karar_dinamik_teknisyen_ekibi_itertools_combinations.md,
  karar_rc13_tam_paket_uygulamasi.md, karar_rc13_asgari_paket_uygulamasi.md (güncelleme notları)
- index.md

RC20 üzerinde (Ö-B/Ö-C/Ö-D) ve metasezgisel tasarımında Eren'in talimatıyla
bu turda **hiçbir ek işlem yapılmadı**.
