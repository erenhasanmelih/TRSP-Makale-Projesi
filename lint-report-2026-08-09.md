# Lint Raporu — 2026-08-09

Tarandı: `raw/` ve `archive/` hariç tüm markdown dosyaları — `sources/` (7), `entities/` (14), `concepts/` (13), `decisions/` (26), `syntheses/` (1) = **61 içerik sayfası**, artı `index.md` ve `log.md` (meta dosyalar, içerik lint kapsamı dışı ama link grafiğine dahil edildi). `CLAUDE.md` şema dosyası olduğu için içerik lint'ine dahil edilmedi.

Yöntem: her sayfanın `Kararlar`/`Related` bölümlerindeki `[[...]]` linkleri çıkarılıp bir link grafiği kuruldu (inbound/outbound), sonra her sayfanın gövde metni bir önceki (2026-08-09 tarihli) genel sentez ve tekil ingest oturumlarındaki bilgiyle karşılaştırıldı.

Toplam bulgu: **16** (Yüksek: 3, Orta: 8, Düşük: 5)

---

## 1. ÇELİŞKİLER

### C1 — [YÜKSEK] `karar_partial_charging_denklemleri_entegrasyonu_plani.md` güncel wiki bilgisiyle çelişiyor

**Dosyalar:** `decisions/karar_partial_charging_denklemleri_entegrasyonu_plani.md` (Gerekçe bölümü) vs `decisions/sorun_kismi_sarj_dinamikleri_kodda_yok.md` (## ÇELİŞKİ güncelleme bölümü, 2026-08-09)

**Sorun:** `karar_partial_charging_denklemleri_entegrasyonu_plani.md`'nin "Gerekçe" bölümü hâlâ şöyle diyor: *"Mevcut EV kodu enerji seviyesini yalnızca tüketim katsayısı × mesafe ile azaltıyor, şarj süresi/hızı dinamiklerini hesaba katmıyor."* Ama aynı gün içinde Stage 2 kod doğrulamasıyla güncellenen `sorun_kismi_sarj_dinamikleri_kodda_yok.md`, `EV_v.1.1.py:165,271`'de `charge_time_i = g_e * (YE[i]-ye[i])` terimiyle **kısmi bir şarj süresi mekanizmasının var olduğunu** tespit etti. İki sayfa şu an birbirine link veriyor ama biri eski/düz iddiayı, diğeri nüanslı/güncel bulguyu taşıyor — okuyucu hangi sayfaya önce rastladığına göre farklı bir gerçeklik algılıyor.

**Düzeltme önerisi:** `karar_partial_charging_denklemleri_entegrasyonu_plani.md`'ye `sorun_kismi_sarj_dinamikleri_kodda_yok.md`'daki gibi bir "## Stage 2 notu" eklenip, hedefin artık "sıfırdan ekleme" değil "`charge_time_i` mekanizmasını Keskin & Çatay (2016)'nın tam formülasyonuna genişletme/doğrulama" olduğu netleştirilmeli.

**Öncelik:** Yüksek — makalede "EV modelinde kısmi şarj yoktu, eklendi" gibi yanlış bir başarı hikâyesi anlatılmasına yol açabilir; aslında kısmi bir mekanizma zaten vardı ve genişletiliyor.

---

## 2. ESKİMİŞ İDDİALAR

### E1 — [ORTA] `sources/2026-08-09-makale_adimlar_ve_duzenlemeler.md`'nin açık sorusu başka bir sayfada zaten cevaplanmış

**Dosyalar:** `sources/2026-08-09-makale_adimlar_ve_duzenlemeler.md` (## Açık konular, satır 58) vs `decisions/sorun_ev_enerji_tuketim_modeli_basitlestirilmis.md` (## Açık konu / Stage 2 doğrulaması)

**Sorun:** Kaynak sayfası hâlâ şunu soruyor: *"'EV kodu çalışamaz durumda' iddiası ... Stage 2'de teyit edilmeli."* Ama Stage 2 zaten yapıldı ve cevap başka bir sayfaya yazıldı: `sorun_ev_enerji_tuketim_modeli_basitlestirilmis.md` bu iddiayı **"abartılı görünüyor ... ama temelsiz değil"** olarak nüanslandırdı. Kaynak sayfa bu çözümü yansıtmıyor, sanki hâlâ açık bir soruymuş gibi duruyor.

**Düzeltme önerisi:** `sources/2026-08-09-makale_adimlar_ve_duzenlemeler.md`'nin "Açık konular" bölümüne "**Stage 2 sonucu (2026-08-09):** bkz. [[sorun_ev_enerji_tuketim_modeli_basitlestirilmis]] — iddia nüanslandırıldı, EV kodu çalışıyor ama enerji modeli basitleştirilmiş." notu eklenmeli.

**Öncelik:** Orta — yanıltıcı değil ama okuyucuyu gereksiz yere "hâlâ çözülmemiş" sanmaya itiyor.

### E2 — [DÜŞÜK] "10-13" / "10-15" düğüm sayısı tutarsızlığı — kaynaksız sayı

**Dosyalar:** `decisions/karar_3_fazli_uygulama_yol_haritasi.md:15`, `decisions/karar_tight_big_m_gecisi_plani.md:17`, `entities/gurobi_mip_cozucusu.md:15`

**Sorun:** `sources/2026-08-09-full_path.md:17` (tek kaynak — `Full Path.docx`) net biçimde **"10-13 düğümde tıkandığını"** söylüyor; `concepts/tight_big_m.md`, `concepts/index_reduction_3b.md`, `decisions/karar_4b_to_3b_index_reduction_plani.md` bu sayıyı doğru aktarıyor. Ama `karar_3_fazli_uygulama_yol_haritasi.md` ve `karar_tight_big_m_gecisi_plani.md` **"10-15"** sayısını kullanıyor; `gurobi_mip_cozucusu.md` bu farkı fark edip *"bazı belgelerde 10-15"* diye parantezle geçiştiriyor ama hangi belgenin bunu söylediğini göstermiyor. Hiçbir `raw/` kaynağında "10-15" ifadesi doğrulanmadı — bu, wiki'nin kendi "kaynaksız iddia yasak" kuralını ihlal eden küçük bir sayı kayması gibi görünüyor.

**Düzeltme önerisi:** İki decision sayfasındaki "10-15" ifadesi "10-13" ile değiştirilmeli (Full Path.docx'e sadık kalınarak), ya da eğer "10-15" gerçekten başka bir raw kaynakta (örn. sonuçlar klasöründeki bir docx) geçiyorsa o kaynak satır referansıyla eklenmeli.

**Öncelik:** Düşük — sayısal fark küçük ve sonuç yorumunu değiştirmiyor, ama tekrarlanan bir tutarsızlık.

---

## 3. YETİM SAYFALAR

### O1 — [YÜKSEK] `sources/2026-08-09-full_path.md` fiilen yetim — projenin "en üst düzey" belgesi hiçbir karar sayfasından link almıyor

**Dosya:** `sources/2026-08-09-full_path.md`

**Sorun:** Bu sayfa kendi metninde *"projenin en üst düzey planlama belgesi"* olarak tanımlanıyor ve 9 farklı `decisions/karar_*_plani.md` sayfası doğrudan bu belgeden türetilmiş (`karar_4b_to_3b_index_reduction_plani`, `karar_tight_big_m_gecisi_plani`, `karar_partial_charging_denklemleri_entegrasyonu_plani`, `karar_klon_dugum_sarj_istasyonu_plani`, `karar_uyumluluk_matrisi_cizelgeleme_plani`, `karar_gunluk_haftalik_planlama_pool_plani`, `karar_hibrit_algoritma_mimari_sirasi`, `karar_pareto_epsilon_constraint_plani`, `karar_3_fazli_uygulama_yol_haritasi`). Ama bu 9 sayfanın **hiçbiri** `Related` bölümünde `[[sources/2026-08-09-full_path]]`'e geri link vermiyor. Tek geri link `concepts/colored_tsp.md`'den geliyor. `index.md` ve `log.md` dışında pratikte izole.

**Düzeltme önerisi:** Yukarıdaki 9 decision sayfasının her birinin `Related` bölümüne `[[sources/2026-08-09-full_path]]` eklenmeli — bu, "bu karar hangi üst düzey plandan geliyor" sorusuna tek tıkla cevap verecek bir hub bağlantısı kurar.

**Öncelik:** Yüksek — wiki'nin "çift-yönlü bağlantı düşüncesi" (Hard Rule #5) kuralının en belirgin ihlali; en kritik kaynak belgesi gezilebilirlik açısından görünmez durumda.

### O2 — [ORTA] `sources/2026-08-09-ek_noktalar_ve_makaleleri.md` zayıf bağlantılı

**Dosya:** `sources/2026-08-09-ek_noktalar_ve_makaleleri.md`

**Sorun:** Sadece `concepts/colored_tsp.md`'den 1 geri link alıyor. Ama içeriği (Q-Learning, VND, ALNS, Filtered Beam Search literatür örnekleri) `concepts/q_learning.md`, `concepts/vnd.md`, `concepts/literatur_alternatif_metasezgiseller.md` sayfalarıyla doğrudan örtüşüyor; bu sayfalar kaynak olarak bu docx'i kullanıyor (frontmatter `source:` alanında) ama `Related` bölümlerinde geri link yok.

**Düzeltme önerisi:** `concepts/q_learning.md`, `concepts/vnd.md`, `concepts/literatur_alternatif_metasezgiseller.md` sayfalarının `Related` bölümlerine `[[sources/2026-08-09-ek_noktalar_ve_makaleleri]]` eklenmeli.

**Öncelik:** Orta.

### O3 — [DÜŞÜK] Yeni sentez sayfası henüz geri link almıyor

**Dosya:** `syntheses/model_kod_farkliliklari_genel_sentez.md`

**Sorun:** Bu oturumda oluşturulan sentez, özetlediği 12 decision/sorun sayfasının (`celiski_single_trip_vs_multitrip`, `celiski_ogle_molasi_zorunlulugu`, vb.) hiçbirinden henüz geri link almıyor — beklenen bir durum (yeni sayfa) ama kalıcı hale gelmemesi için düzeltilmeli.

**Düzeltme önerisi:** Bu 12 sayfanın her birinin `Related` bölümüne `[[syntheses/model_kod_farkliliklari_genel_sentez]]` eklenmeli.

**Öncelik:** Düşük — henüz yeni, ama bir sonraki lint pass'e kadar kalırsa "orta"ya çıkar.

---

## 4. EKSİK KAVRAM SAYFALARI

### K1 — [ORTA] MTZ (Miller-Tucker-Zemlin alt-tur önleme) kendi sayfası yok

**Geçtiği sayfalar (5):** `sources/2026-08-09-ek_noktalar_ve_makaleleri.md:35`, `sources/2026-08-09-makale_adimlar_ve_duzenlemeler.md:23,44,57`, `concepts/literatur_alternatif_metasezgiseller.md:15`, `concepts/tight_big_m.md:17`, `decisions/karar_tight_big_m_gecisi_plani.md:13`

**Sorun:** MTZ, alt-tur (sub-tour) önleme kısıtı olarak birden fazla sayfada anılıyor ve `tau` (zaman ilerleme) değişkeniyle dolaylı ilişkisi ("kodda `tau` üzerinden zaten var olup olmadığı Stage 2'de doğrulanmalı" — `makale adımlar ve düzenlemeler.docx` kaynaklı açık soru) hâlâ **doğrulanmamış**. Kendi `concepts/` sayfası yok; şu an `literatur_alternatif_metasezgiseller.md` içinde bir madde olarak geçiyor ama bu sayfa kendi tanımı gereği "aktif geliştirme kararı olmayan" referans sayfası — MTZ'nin kodla ilişkisi (var mı yok mu) bu sayfanın kapsamı dışında kalıyor.

**Düzeltme önerisi:** `concepts/mtz_alt_tur_onleme.md` adında yeni bir sayfa açılmalı; `EV_v.1.1.py`/`CV_model_gurobi_exact.py`'deki `c8_zaman_ilerleme` kısıtının MTZ ile matematiksel ilişkisi Stage 3 ingest'inde doğrulanmalı (bu, `makale adımlar ve düzenlemeler.docx`'teki açık sorunun cevabı olur).

**Öncelik:** Orta — hem eksik sayfa hem de arkasında çözülmemiş bir "Açık konu" var.

### K2 — [ORTA] `charge_time_i` mekanizması 6+ sayfada tekrar tekrar açıklanıyor, kendi sayfası yok

**Geçtiği sayfalar (6):** `sources/2026-08-09-ev_v1_1.md`, `concepts/partial_recharging.md`, `decisions/sorun_kismi_sarj_dinamikleri_kodda_yok.md`, `entities/degisken_yakit_enerji_izleme.md`, `entities/model_karar_degiskenleri_ve_parametreleri.md`, `decisions/sorun_ev_enerji_tuketim_modeli_basitlestirilmis.md`

**Sorun:** EV modelinin kısmi şarj süresini zaman eksenine yansıtan `charge_time_i = g_e * (YE[i]-ye[i])` formülü, wiki'nin en sık atıfta bulunulan kod mekanizmalarından biri ama her sayfada kısaca yeniden özetleniyor — tek bir kanonik `entities/` sayfası yok. Bu, gelecekte formülün nüansı (örn. Keskin & Çatay uyumu doğrulandığında) güncellenmesi gerektiğinde 6 farklı sayfanın senkron tutulması riskini doğuruyor.

**Düzeltme önerisi:** `entities/degisken_charge_time_i.md` oluşturulup diğer 6 sayfadaki tekrar eden açıklamalar bu sayfaya yönlendirilmeli (link + kısa özet bırakılabilir).

**Öncelik:** Orta.

### K3 — [DÜŞÜK] `L[i,t]` (kullanılmayan karar değişkeni) belgelenmemiş

**Geçtiği sayfalar (3):** `sources/2026-08-09-cv_model_gurobi_exact.md`, `sources/2026-08-09-ev_v1_1.md`, `entities/model_karar_degiskenleri_ve_parametreleri.md` (tabloda)

**Sorun:** Hem CV hem EV kodunda tanımlı ama hiçbir kısıtta kullanılmayan `L[i,t]` değişkeni, `alpha[Fc,Vc]`'nin aksine (ki o `sorun_cv_kullanilmayan_istasyon_parametreleri.md` sayfasını aldı) kendi sayfasına sahip değil — sadece geçişte anılıyor.

**Düzeltme önerisi:** Ya `sorun_cv_kullanilmayan_istasyon_parametreleri.md` kapsamı genişletilip başlığı "Kullanılmayan Değişkenler (CV+EV)" yapılarak `L[i,t]` de eklenmeli, ya da ayrı küçük bir sayfa açılmalı.

**Öncelik:** Düşük — ölü kod, mimari etkisi yok, ama iki modelde ortak olması ilginç bir gözlem.

### K4 — [ORTA] EV'nin sadece 3 örnekte test edilmesi vs CV'nin tüm 25 örnekte — belgelenmemiş metodolojik asimetri

**Geçtiği sayfalar (2):** `entities/model_calistirma_parametreleri_ev.md`, `sources/2026-08-09-ev_v1_1.md` (## Açık konular)

**Sorun:** `EV_v.1.1.py`'de `TARGET_INSTANCE_SEQUENCE = ["R15","RC15","RC13"]` sabiti, EV modelinin varsayılan olarak sadece 3 problem örneğiyle çalıştırılmasına neden oluyor; CV modeli ise `select_instances()` ile interaktif olarak tüm 25 örnekten seçim yapabiliyor. Bu, gelecekteki CV vs EV Pareto/performans karşılaştırmasının (bkz. `karar_pareto_epsilon_constraint_plani.md`) **eşit olmayan bir örneklem üzerinden** yapılma riskini taşıyor — ama bu risk hiçbir `decisions/` sayfasında ayrı bir madde olarak işlenmemiş, sadece bir "Açık konular" dipnotu olarak kalmış.

**Düzeltme önerisi:** `decisions/sorun_ev_instance_kapsami_sinirli.md` gibi yeni bir sorun sayfası açılıp `karar_pareto_epsilon_constraint_plani.md`'ye çapraz link verilmeli — Pareto analizi yapılmadan önce EV'nin de tüm örneklerde (ya da en azından CV ile aynı alt kümede) çalıştırılması gerektiği not edilmeli.

**Öncelik:** Orta — şu an sonuç yok ama gelecekteki bir karşılaştırmanın geçerliliğini doğrudan etkileyebilir.

---

## 5. TEK-YÖNLÜ CROSS-REFERENCELAR

### X1 — [ORTA] `karar_dinamik_teknisyen_ekibi_itertools_combinations.md` → `index_reduction_3b.md` / `uyumluluk_matrisi.md` tek yönlü

**Sorun:** `karar_dinamik_teknisyen_ekibi_itertools_combinations.md`, index-reduction planının "statik eşleştirme" varsayımıyla kendi "dinamik ekip oluşturma" bulgusu arasındaki gerilimi açıkça tartışıyor ve her iki sayfaya link veriyor. Ama ne `concepts/index_reduction_3b.md` ne `concepts/uyumluluk_matrisi.md` bu gerilimden bahsediyor ya da geri link veriyor — okuyucu index_reduction_3b sayfasına önce girerse bu açık riskten habersiz kalıyor.

**Düzeltme önerisi:** `index_reduction_3b.md`'ye "## Bilinen risk" bölümü eklenip `[[karar_dinamik_teknisyen_ekibi_itertools_combinations]]`'a link verilmeli (zaten `karar_4b_to_3b_index_reduction_plani.md`'de bu risk var, ama concept sayfasının kendisinde yok).

**Öncelik:** Orta.

### X2 — [ORTA] `karar_ev_feasibility_gurobi_tuning_ve_diagnostik.md` → `karar_4b_to_3b_index_reduction_plani.md` tek yönlü

**Sorun:** `karar_ev_feasibility_gurobi_tuning_ve_diagnostik.md`, Gurobi tuning'in yapısal düzeltmelere (index reduction, tight Big-M) kıyasla "geçici bir workaround" olduğunu açıklarken her iki plana link veriyor. `karar_tight_big_m_gecisi_plani.md` geri link veriyor ama `karar_4b_to_3b_index_reduction_plani.md` vermiyor.

**Düzeltme önerisi:** `karar_4b_to_3b_index_reduction_plani.md`'nin `Related` bölümüne `[[karar_ev_feasibility_gurobi_tuning_ve_diagnostik]]` eklenmeli.

**Öncelik:** Orta.

### X3 — [DÜŞÜK] Diğer küçük tek-yönlü xref'ler (toplu)

- `entities/topsis.md` frontmatter'da kaynak olarak `sources/2026-08-09-makale_adimlar_ve_duzenlemeler.md`'yi gösteriyor ama `Related`'da link yok (kardeşi `entities/catboost.md` bu linki veriyor, asimetri var).
- `entities/model_calistirma_parametreleri_ev.md` → `entities/degisken_route_start_route_end_ev.md` tek yönlü.
- `entities/python_gurobipy.md` → `entities/model_karar_degiskenleri_ve_parametreleri.md` tek yönlü.
- `entities/degisken_x_arc_tahsisi.md` ↔ `decisions/karar_dinamik_teknisyen_ekibi_itertools_combinations.md` — sadece degisken_x_arc_tahsisi.md link veriyor, karşı sayfa vermiyor.

**Düzeltme önerisi:** Her birine karşılıklı `[[...]]` eklenmeli; düşük öncelikli olduklarından tek seferde toplu düzeltilebilir.

**Öncelik:** Düşük.

---

## 6. KAYNAK BOŞLUKLARI

### S1 — [YÜKSEK] "Planlanan mimari kararlar" kümesi (9 sayfa) tamamen tek bir belgeye dayanıyor

**Dosyalar:** `karar_4b_to_3b_index_reduction_plani.md`, `karar_tight_big_m_gecisi_plani.md`, `karar_partial_charging_denklemleri_entegrasyonu_plani.md`, `karar_klon_dugum_sarj_istasyonu_plani.md`, `karar_uyumluluk_matrisi_cizelgeleme_plani.md`, `karar_gunluk_haftalik_planlama_pool_plani.md`, `karar_hibrit_algoritma_mimari_sirasi.md`, `karar_pareto_epsilon_constraint_plani.md`, `karar_3_fazli_uygulama_yol_haritasi.md`

**Sorun:** Bu 9 sayfanın `Sources` alanı **sadece** `raw/Yönergelerimiz/Full Path.docx`'e (bazıları ek olarak `makale adımlar ve düzenlemeler.docx`'e) dayanıyor. Henüz kodda uygulanmadıkları için bu doğal, ama makalenin "Algoritmik Geliştirmeler" ve "Pareto Optimizasyonu" bölümlerinin **tamamı** tek bir Word belgesindeki plana dayanıyor — ikinci bir doğrulama (örn. kullanıcıyla sözlü teyit, önceki taslak sürümleri, literatür makalelerinin orijinalleri) yok.

**Düzeltme önerisi:** Makale yazımına geçmeden önce bu 9 kararın en azından kullanıcıyla bir "hâlâ geçerli mi" teyidi yapılması, özellikle `karar_hibrit_algoritma_mimari_sirasi.md` (mimarinin omurgası) için önerilir. Ek doğrulama kaynağı olarak Full Path.docx'in atıf verdiği makalelerin (Acar & Altın 2025, Acar et al. 2025, Yıldız vd. 2025, Keskin & Çatay 2016, Cordeau vd. 2002) orijinal metinlerinin ileride ayrıca ingest edilmesi düşünülebilir.

**Öncelik:** Yüksek — makalenin en özgün/karmaşık teknik katkısı (Q-Learning+VND mimarisi) tek kaynağa dayanıyor.

### S2 — [ORTA] "Dinamik tahminleme" kümesi (6 sayfa) tek belgeye dayanıyor

**Dosyalar:** `karar_3_asamali_rolling_horizon_sistem_mimarisi.md`, `karar_iptal_olasiligi_on_filtreleme_plani.md`, `karar_sentetik_veri_uretici_solomon_plani.md`, `concepts/rolling_horizon.md`, `concepts/iptal_olasiligi_tahmini.md`, `concepts/warm_start.md` (kısmen)

**Sorun:** Tamamı `dinamik tahminleme adımları ve veri.docx`'e dayanıyor; CatBoost/TOPSIS entegrasyonunun hiçbir kod karşılığı yok (frontmatter'larda `status: taslak` olarak zaten işaretli — bu iyi bir pratik, ama küme genelinde tekrar ediyor).

**Düzeltme önerisi:** Özellikle "%80 iptal eşiği" gibi somut, kalibre edilmemiş bir parametrenin (`iptal_olasiligi_tahmini.md`'de zaten "Açık konular" olarak not düşülmüş) hangi veriyle doğrulanacağı netleşmeden makaleye sayısal biçimde girmemesi önerilir.

**Öncelik:** Orta.

### S3 — [DÜŞÜK] `karar_ev_teknisyen_cakisma_onleme_mekanizmasi.md` — kritik bulgu, tek okumaya dayanıyor

**Dosya:** `decisions/karar_ev_teknisyen_cakisma_onleme_mekanizmasi.md`

**Sorun:** Bu sayfa (ve ona dayanan CV mantık boşluğu iddiası) sadece `EV_v.1.1.py:225-299`'un tek seferlik okunmasına dayanıyor. CV tarafında "bu koruma yok" iddiası da dolaylı — CV kodunda `route_start`/`ord_*` benzeri bir yapının **aranıp bulunamadığı** ayrı bir negatif-doğrulama adımı olarak belgelenmemiş, sadece "CV kodu da aynı ekip oluşturma mantığını kullanıyor ama bu çakışma koruması olmadan" deniyor.

**Düzeltme önerisi:** `CV_model_gurobi_exact.py`'de `grep`/tam metin taramasıyla `route_start`, `ord_`, `crew_members` benzeri hiçbir yapının olmadığı açıkça (satır aralığı olmasa da "aranmış ve bulunamamış" notuyla) teyit edilip sayfaya eklenmeli — bu, sentez sayfasındaki "yüksek öncelik" önerisinin (CV'ye portlama) gerekçesini sağlamlaştırır.

**Öncelik:** Düşük (bulgunun kendisi muhtemelen doğru, ama teyit adımı eksik).

---

## Öncelik Özeti

| Öncelik | Sayı | Bulgular |
|---|---|---|
| Yüksek | 3 | C1, O1, S1 |
| Orta | 8 | E1, O2, K1, K2, K4, X1, X2, S2 |
| Düşük | 5 | E2, O3, K3, X3, S3 |
| **Toplam** | **16** | |

## Önerilen sonraki adımlar (öncelik sırasıyla)

1. `karar_partial_charging_denklemleri_entegrasyonu_plani.md`'yi Stage 2 bulgusuyla güncelle (C1).
2. 9 "Planlanan mimari kararlar" sayfasına `[[sources/2026-08-09-full_path]]` geri linkini ekle — hem O1'i hem S1'in görünürlüğünü çözer.
3. Makale yazımına geçmeden önce Full Path.docx'teki 9 kararı kullanıcıyla teyit et (S1).
4. Geri kalan tek-yönlü xref ve eksik-kavram sayfası düzeltmelerini bir sonraki bakım oturumunda toplu işle.
