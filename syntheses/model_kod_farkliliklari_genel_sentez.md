---
title: Model↔Kod Farklılıkları — Genel Sentez
tags: [sentez, model-kod-uyumsuzluğu, kritik, makale-öncesi]
source: sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar.md; raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Model↔Kod Farklılıkları — Genel Sentez

## Amaç

`kodda ve matematiksel modeldeki farklılıklar.docx`'in tespit ettiği 10 maddelik liste, Stage 2'de (`raw/CV_model_gurobi_exact.py` ve `raw/EV_v.1.1.py`'nin satır satır okunması) kod ile karşılaştırılarak doğrulandı. Bu sayfa, o doğrulama sürecinin sonuçlarını tek bir yerde topluyor: hangi iddia doğrulandı, hangisi nüanslandı, hangisi tamamen çürütüldü — ve makale öncesi hangi maddelerin kapatılması gerektiğine dair bir önceliklendirme sunuyor.

## Özet tablo — 13 madde, 4 kategori

| # | Madde | Kategori | Stage 2 doğrulama durumu | Kaynak sayfa |
|---|---|---|---|---|
| 1 | Single-trip (model) vs multi-trip (docx iddiası) | Çelişki (docx↔kod) | **Çürütüldü** — kod aslında tek-sefer, docx'ün tarif ettiği `c4_multitrip_{v}` kısıtı kodda yok | [[celiski_single_trip_vs_multitrip]] |
| 2 | Öğle molası zorunlu (model) vs opsiyonel (kod) | Çelişki (model↔kod) | **Doğrulandı** — `mola_max1_{t}`, hem CV hem EV'de `<=1` | [[celiski_ogle_molasi_zorunlulugu]] |
| 3 | Şarj/yakıt istasyonları modelde var, kodda yok | Eksiklik | **Kısmen doğrulandı** — CV'de tam eksik; EV'de `S_set` ile kısmen var | [[sorun_sarj_yakit_istasyonlari_kodda_yok]] |
| 4 | Kısmi şarj dinamikleri kodda yok | Eksiklik | **Nüanslandı** — EV'de `charge_time_i` mekanizması var (tam Keskin&Çatay formülasyonu değil) | [[sorun_kismi_sarj_dinamikleri_kodda_yok]] |
| 5 | Mola-istasyon bağıntısı (Kısıt 10/11) kodda yok | Eksiklik | Doğrulanmadı ayrıca — istasyon yapısı zaten eksik olduğu için otomatik doğru | [[sorun_sarj_yakit_istasyonlari_kodda_yok]] |
| 6 | Hardcoded mola parametreleri | Eksiklik/kısıt | **Doğrulandı** — `break_duration=3600` vb. her iki modelde sabit | [[sorun_hardcoded_mola_parametreleri]] |
| 7 | EV enerji tüketim modeli aşırı basitleştirilmiş | Eksiklik | **Doğrulandı** — `h_e * mesafe`, yüke/hıza duyarsız | [[sorun_ev_enerji_tuketim_modeli_basitlestirilmis]] |
| 8 | CV'de kullanılmayan istasyon parametreleri (Fc, alpha, g_c, k, lc0) | Eksiklik (kod kanıtı) | **Doğrulandı** — madde 3'ün somut kod kanıtı, yarım kalmış iskelet | [[sorun_cv_kullanilmayan_istasyon_parametreleri]] |
| 9 | Dinamik teknisyen ekibi (itertools.combinations) | Kod-only ek esneklik | **Doğrulandı** — CV+EV ortak | [[karar_dinamik_teknisyen_ekibi_itertools_combinations]] |
| 10 | Molasız erken dönüş kuralı | Kod-only ek esneklik | **Doğrulandı** — çelişki #2'yi telafi ediyor | [[karar_molasiz_erken_donus_kurali_kod]] |
| 11 | Operasyonel zaman kaydırma (+28800) | Kod-only, zararsız | **Doğrulandı** — saf raporlama, model-kod çelişkisi değil | [[karar_operasyonel_zaman_kaydirma_format_time]] |
| 12 | EV teknisyen çakışma önleme mekanizması | Kod-only, yönergede yok | **Yeni bulgu (Stage 2)** — CV'de karşılığı yok, potansiyel CV mantık boşluğu | [[karar_ev_teknisyen_cakisma_onleme_mekanizmasi]] |
| 13 | EV feasibility-odaklı Gurobi tuning + IIS diagnostik | Kod-only, workaround | **Yeni bulgu (Stage 2)** — yapısal düzeltme değil, geçici çözücü ayarı | [[karar_ev_feasibility_gurobi_tuning_ve_diagnostik]] |

(Madde 10'daki orijinal docx numaralandırmasındaki "otomatik docx raporlama" [[karar_ev_otomatik_docx_raporlama]] bu tabloya dahil edilmedi çünkü model-kod farkı değil, salt bir çıktı-üretim mekanizması açıklaması.)

## Kategorilere göre değerlendirme

### A) Gerçek çelişkiler (2 madde) — makale öncesi karar gerektirir

1. **Öğle molası zorunlu/opsiyonel** (#2): Bu, iş hukuku açısından ciddi bir tutarsızlık. Model molayı zorunlu tutarken kod opsiyonel bırakıyor ve bunu "molasız erken dönüş" kısıtıyla telafi ediyor. **Öneri:** Bu bilinçli bir gevşetme (relaxation) olarak mı kalacak yoksa model kodun `=1` versiyonuna mı çekilecek — makalede açıkça gerekçelendirilmeli. Şu an sessizce iki farklı davranış var.
2. **Single-trip/multi-trip** (#1): Bu artık model↔kod çelişkisi değil, **docx↔kod** çelişkisi — kodun kendisi zaten single-trip ve modelle uyumlu. Docx'ün yanlış tarif ettiği anlaşılıyor. **Öneri:** Yönerge belgesi düzeltilmeli veya en azından bu ingest'in bulgusu yönergeyi yazanla paylaşılmalı; makalede bu madde hiç sorun değil.

### B) Modelde olup kodda eksik (3 ana madde, EV/CV'ye göre değişken)

- İstasyon yapısı (#3, #5, #8): **CV'de tam eksik ve hatta yarım bırakılmış kod iskeleti var** (`Fc`/`alpha` kullanılmıyor). **EV'de kısmen mevcut.** Bu, CV ve EV modellerinin makale olgunluk seviyesinin eşit olmadığını gösteriyor — CV modeli istasyon açısından EV'den daha geri.
- Kısmi şarj dinamikleri (#4): Sadece EV'yi ilgilendiriyor, CV'de yakıt istasyonu kavramı zaten daha az kritik (yakıt istasyonları EV'nin şarj süresi kısıtı kadar operasyonel darboğaz yaratmıyor). EV'deki mekanizma "yoktur" değil "basitleştirilmiş" — [[karar_partial_charging_denklemleri_entegrasyonu_plani]] bu boşluğu tam formülasyonla kapatmayı planlıyor.
- EV enerji tüketim modeli (#7): Hem model hem kod aynı basitleştirmeyi paylaşıyor (bu bir çelişki değil, ortak bir sınırlama) — makalede "gelecek çalışma" olarak konumlandırılabilir.

### C) Kodun modele eklediği esneklikler (5 madde) — çoğu zararsız, ikisi dikkat gerektiriyor

- Zararsız/faydalı: dinamik ekip oluşturma (#9), zaman kaydırma (#11), Gurobi tuning (#13) — bunlar modelin matematiksel doğruluğunu bozmuyor, sadece operasyonel/pratik katman.
- **Dikkat gerektiren:** EV'nin teknisyen çakışma önleme mekanizması (#12) **CV'de yok**. Her iki model de aynı `itertools.combinations` ekip oluşturma mantığını paylaştığı için, CV'de aynı teknisyenin iki farklı ekipte aynı gün çakışan saatlerde görünmesi **matematiksel olarak engellenmiyor**. Bu, EV'de bilinçli olarak eklenmiş ama CV'ye taşınmamış bir düzeltme gibi görünüyor — muhtemelen bir **kod tutarsızlığı/eksik port**, tasarım kararı değil.
- Molasız erken dönüş (#10) yalnızca çelişki #2'nin var olması nedeniyle gerekli; çelişki #2 çözülürse bu kısıt da anlamını yitirir.

## Makale öncesi önceliklendirme (öneri)

| Öncelik | Madde | Gerekçe |
|---|---|---|
| Yüksek | CV'ye teknisyen çakışma önleme mekanizmasının portlanması (#12) | Sonuçların geçerliliğini etkileyen sessiz bir mantık boşluğu — CV çözümleri fiziksel olarak imkânsız çizelgeler içeriyor olabilir |
| Yüksek | Öğle molası zorunlu/opsiyonel kararının netleştirilmesi (#2) | Makalede model formülasyonu ile kod davranışı tutarsız görünmemeli |
| Orta | Docx'teki multi-trip iddiasının düzeltilmesi/not düşülmesi (#1) | Yanlış yönerge bilgisi, gelecekte tekrar kafa karışıklığı yaratabilir |
| Orta | CV istasyon iskeletinin tamamlanması ya da temizlenmesi (#3/#8) | Kullanılmayan parametreler ya işlevselleştirilmeli ya da kodda "planlanmış ama iptal edilmiş" olarak belgelenmeli |
| Düşük | Mola parametrelerinin parametrikleştirilmesi (#6) | Duyarlılık analizi için faydalı ama makalenin ana bulgularını etkilemiyor |
| Düşük | EV enerji modelinin doğrusal olmayan hale getirilmesi (#7) | Bilinen sınırlama, "gelecek çalışma" olarak makalede belirtilebilir |

## Genel gözlem

Stage 2 doğrulaması, docx'ün orijinal 10 maddesinden **hiçbirinin olduğu gibi doğru olmadığını** gösterdi: 6 madde nüanslandı (kısmen doğru/kısmen yanlış), 1 madde tamamen çürütüldü (multi-trip), ve kod tabanının kendisi 2 yeni, docx'te hiç anılmayan bulgu ortaya çıkardı (#12, #13). Bu, `raw/Yönergelerimiz/` altındaki yönerge belgelerinin **kodun geçmiş bir sürümünü** tarif ediyor olabileceğine işaret ediyor — dosya tarihleri bunu doğrulamasa da (docx'ler Python dosyalarından ~15 ay sonra yazılmış), belgenin en azından bazı bölümlerinin güncel kodu yansıtmadığı açık.

**Öneri:** Yönerge belgeleri (özellikle `kodda ve matematiksel modeldeki farklılıklar.docx`) kullanıcıyla birlikte gözden geçirilip güncel kod durumuna göre revize edilmeli, ya da en azından makalede hangi kaynağın (docx mi, kod mu) otoriter kabul edildiği açıkça belirtilmeli.

## Sources

- [[sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar]]
- [[sources/2026-08-09-cv_model_gurobi_exact]]
- [[sources/2026-08-09-ev_v1_1]]
- `raw/CV_model_gurobi_exact.py`
- `raw/EV_v.1.1.py`

## Related

- [[celiski_single_trip_vs_multitrip]]
- [[celiski_ogle_molasi_zorunlulugu]]
- [[sorun_sarj_yakit_istasyonlari_kodda_yok]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
- [[sorun_hardcoded_mola_parametreleri]]
- [[sorun_ev_enerji_tuketim_modeli_basitlestirilmis]]
- [[sorun_cv_kullanilmayan_istasyon_parametreleri]]
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]
- [[karar_molasiz_erken_donus_kurali_kod]]
- [[karar_operasyonel_zaman_kaydirma_format_time]]
- [[karar_ev_teknisyen_cakisma_onleme_mekanizmasi]]
- [[karar_ev_feasibility_gurobi_tuning_ve_diagnostik]]
