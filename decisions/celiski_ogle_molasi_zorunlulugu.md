---
title: ÇELİŞKİ — Öğle Molası Zorunlu (Model) vs Opsiyonel (Kod)
tags: [çelişki, kısıt, mola, kritik]
source: raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx
date: 2026-08-09
status: güncel
---

# ÇELİŞKİ — Öğle Molası Zorunlu (Model) vs Opsiyonel (Kod)

## ÇELİŞKİ

**Matematiksel model tarafı:** Kısıt (12), göreve çıkan her teknisyen için mutlaka **tam olarak bir** öğle yemeği molası atanmasını `=1` eşitliğiyle zorunlu kılar.

**Kod tarafı:** `mola_max1_{t}` kısıtı `<=1` şeklinde modellenmiş — yani mola kullanmak **zorunlu değil**, en fazla bir kez kullanılabilecek bir opsiyon.

## Neden önemli

Bu fark, gün içi rotanın toplam süresini ve teknisyenlerin yasal mola hakkını doğrudan etkiler. Kodun opsiyonel davranışı, kısa rotalarda mola atlanarak daha hızlı çözüm bulunmasını kolaylaştırıyor olabilir (bir tür gevşetme/relaxation), ama bu iş hukuku açısından model varsayımıyla çelişiyor.

## İlişkili kod kararı

Kodun `mola_yoksa_erken_donus_{i}_{v}_{t}` kısıtı bu opsiyonelliği telafi etmeye çalışıyor: mola kullanılmadıysa depoya dönüşü daha erken saate zorluyor (bkz. [[karar_molasiz_erken_donus_kurali_kod]]). Model tarafında mola zaten zorunlu olduğundan böyle bir telafi kısıtına ihtiyaç yok.

## Stage 2 kod doğrulaması (2026-08-09)

Doğrulandı — kod, docx'ün tarifiyle tam örtüşüyor: `mola_max1_{t}` kısıtı hem CV (`CV_model_gurobi_exact.py:88-96`) hem EV (`EV_v.1.1.py:177-183`) dosyalarında `sum_w <= gp.quicksum(x[0,i,v,t] ...)` şeklinde, yani mola göstergesinin toplamı en fazla 1 (opsiyonel), zorunlu değil.

## ÇÖZÜLDÜ (2026-08-22, kısmen — model belgesi kodun davranışına göre yeniden yazıldı)

Yeni matematiksel model belgesi ("Matematiksel Model - CV ve EV.docx", Bölüm 3.4.1, Kısıt CV-13 açıklaması) bu çelişkiyi doğrudan ele alıyor ve **kodun gerçek davranışını esas alarak modeli güncelliyor**:

> "Kısıt (CV-13), önceki sürümde eşitlik (=) olarak tanımlanan zorunlu öğle molası kuralını eşitsizliğe (≤) çevirerek molayı opsiyonel hale getirir; bu, `CV_model_gurobi_exact.py`'deki `mola_max1_{t}` kısıtının biçimsel karşılığıdır."

Yani çözüm yönü, önceki analizlerin varsaydığının **tersi**: kod değiştirilip modele (zorunlu `=1`) uydurulmadı; model belgesi güncellenip kodun (opsiyonel `<=1`) gerçek davranışına uyduruldu. Yeni `raw/CV_model_gurobi_exact.py` da bu kuralı aynen koruyor (`CV13_mola_max_{kk_name[kk]}`, satır 279-287, hâlâ `<=`).

**EV tarafında zaten çelişki yoktu** ve hâlâ yok: EV modeli hem eski hem yeni kodda zorunlu molayı (`==`) koruyor (`EV12_mola_zorunlu_{kk_name[kk]}`, `EV_v.1.1.py:280-287`), yeni model belgesi de bunu EV-12 olarak `==` ile resmileştirmiş ("EV: zorunlu (=EV-12, kodla tutarlı)").

**Sonuç:** CV tarafındaki model↔kod çelişkisi, CLAUDE.md'nin öngördüğü "çözüldü" notuyla birlikte burada kalıcı olarak kayıt altına alınıyor (silinmiyor) — çözüm yöntemi not edilmeye değer bir örnek: bazı model↔kod çelişkileri kodun modele değil, modelin koda uydurulmasıyla kapanabiliyor.

## GÜNCELLEME (2026-08-23) — sayım TABANI değişti, CV/EV ayrımı korundu

[[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] uygulanırken bu kısıtın
**sağ tarafı** değişmek zorunda kaldı. Eski hâlde sayım tabanı **sefer sayısı** idi:

```python
# ESKİ  (CV-13)  sum_w <= Σ_j x[0,j,k]        # = o günkü sefer sayısı
# ESKİ  (EV-12)  sum_w == Σ_j x[0,j,k]
```

Yani model, 2 sefer yapan bir kaynağa 2 mola *veriyordu* (EV'de zorunlu kılıyordu).
Ama mola penceresi günde **tek ve sabittir** (`el=14400`, `ll=21600`;
`raw/xml_data_loader.py:226-227`) ve CV-10/CV-12 (EV-9/EV-11) iki molanın da aynı
`[el, ll]` penceresini işgal etmesini dayatır. Sefer sırası kısıtı (CV-29/EV-28)
yokken bu tutarsızlık **gizli** kalıyordu; eklendiğinde:

```
1. sefer molası ⇒ τ[e_1] ≥ ll ;  2. sefer molası ⇒ τ[o_2] ≤ el
CV-29/EV-28     ⇒ τ[e_1] ≤ τ[o_2]     ⇒  ll ≤ el  ⇒ ÇELİŞKİ
```

EV tarafında bu, modeli infeasible **yapmaz** — Gurobi sessizce `u[2,k]=0` seçer ve
EV fiilen tek-seferli modele geri dönerdi (düzeltme ölçülemez hâle gelirdi).
Bu yüzden sayım tabanı **"aktif kaynak"a** çevrildi:

```python
# YENİ (CV-13)  sum_w <= z[kk]         # raw/CV_model_gurobi_exact.py:431-450
# YENİ (EV-12)  sum_w == z_veh[kk]     # raw/EV_v.1.1.py:403-424
```

**Bu sayfanın ana çelişkisi bundan etkilenmez:** CV'nin opsiyonel (`≤`) / EV'nin
zorunlu (`==`) ayrımı **aynen korunmuştur**; değişen yalnızca sağ taraftaki
sayım tabanıdır. Fiziksel yorum da düzelmiştir: "günde kaynak başına en fazla /
tam olarak **bir** öğle molası".

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- `raw/CV_model_gurobi_exact.py:431-450` (CV-13, yeni `≤ z[kk]` biçimi, 2026-08-23)
- `raw/EV_v.1.1.py:403-424` (EV-12, yeni `== z_veh[kk]` biçimi, 2026-08-23)
- `raw/CV_model_gurobi_exact.py:88-96` (eski, 2026-08-09 hâli)
- `raw/EV_v.1.1.py:177-183` (eski, 2026-08-09 hâli)
- `raw/CV_model_gurobi_exact.py:279-287` (yeni, CV13_mola_max, 2026-08-22)
- `raw/EV_v.1.1.py:280-287` (yeni, EV12_mola_zorunlu, 2026-08-22)
- `yeni dosyalarım/Matematiksel_Model_rev_v1.1/Matematiksel Model - CV ve EV.docx` (Kısıt CV-13, EV-12 açıklamaları)

## Related

- [[karar_rc13_tam_paket_uygulamasi]] (Ö3/Ö4'ün CV'ye taşınamamasının doğrudan sonucu: min_veh ve bwp, EV-12'nin zorunlu molasına dayanır, CV-13'ün opsiyonelliği bu argümanı geçersiz kılar)
- [[sorun_rc20_darbogaz_kok_neden_analizi]] (§2.2 — CV-13'ün opsiyonelliği CV'ye **kapasite avantajı sağlamaz**, çünkü CV-14 molasız kaynağı `ll`'ye kadar depoya döndürür: molalı 25 200 s vs. molasız 21 600 s. Yani "EV zorunlu / CV opsiyonel" ayrımı fizibilite duvarını **değiştirmiyor**)
- [[sorun_rc13_darbogaz_kok_neden_analizi]] (RC13'te 6 müşterinin zorunlu öğleden-sonra kaydırması + zorunlu mola, sırt-çantası alt problemine yol açan asıl etken)
- [[karar_molasiz_erken_donus_kurali_kod]]
- [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]]
- [[sorun_coklu_sefer_zaman_sirasi_ihlali]]
- [[sorun_hardcoded_mola_parametreleri]]
- [[sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar]]
- [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]]
- [[sources/2026-08-22-ev_v1_1_rewrite]]
