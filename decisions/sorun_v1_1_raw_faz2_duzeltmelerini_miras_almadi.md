---
title: Sorun (Kritik, v1.1) — Yeni raw/ Kodu Faz 2'nin A1/A7 Düzeltmelerini Miras Almadı (DOĞRULANDI, ÇÖZÜLDÜ)
tags: [sorun, kritik, regresyon, ev, cv, sarj-modeli, yakit-modeli, v1.1, dogrulandi, cozuldu]
source: raw/EV_v.1.1.py; raw/xml_data_loader.py; raw/CV_model_gurobi_exact.py
date: 2026-08-22
status: güncel
---

# Sorun (Kritik, v1.1) — Yeni raw/ Kodu Faz 2'nin A1/A7 Düzeltmelerini Miras Almadı

## Önemli not (kapsam sınırı)

Bu sayfa **statik kod okumasına dayalı bir gözlemdir, uçtan uca test/Gurobi koşumuyla doğrulanmamıştır**. Kütüphaneci ajan (bu sayfayı yazan) matematiksel/algoritmik doğruluk hakkında hüküm vermez — bu bulgunun gerçek bir hata mı yoksa yanlış okuma mı olduğunun teyidi `trsp-exact-model-mimari` uzman ajanına veya Eren'e bırakılmıştır. `status: taslak` bu yüzden bilinçli seçildi.

## Bulgu 1 — A1 (EV şarj c20/c21 çakışması) yeniden mi ortaya çıktı?

Faz 2'de (bkz. [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]) tespit edilen kök sorun şuydu: istasyon düğümlerinde varış-enerjisi zincirine (`ye[i]` tabanlı kısıt) dayalı bir üst sınır kısıtı, ayrılış-enerjisi zincirine (`YE[i]` tabanlı, şarj sonrası) dayalı kısıtı her zaman eziyor, böylece şarj edilen enerji bir sonraki bacağın tüketim hesabına hiç yansımıyordu. Düzeltme, istasyon düğümlerinde `ye`-tabanlı kısıtı **atlamaktı** (`if i in S_set: continue`, `src/EV_v_1_1_fixed.py:472-483`).

**Yeni `raw/EV_v.1.1.py` (2026-08-22) aynı ikili yapıyı kullanıyor** — EV-18 (`ye[i]` tabanlı) ve EV-19 (`YE[i]` tabanlı) kısıtları `EV_v.1.1.py:330-346` içinde, **istasyon düğümleri için hiçbir atlama/istisna olmadan** tüm `(i,j) ∈ A` çiftleri için yazılıyor:

```python
for i in Np:
    for j in Np:
        if (i, j) not in A:
            continue
        for kk in K:
            ...
            m.addConstr(ye[j] <= ye[i] - (h_e*d[i,j])*x[i,j,kk] + Qk*(1-x[i,j,kk]), name=f"EV18_ub_...")
            ...
            m.addConstr(ye[j] <= YE[i] - (h_e*d[i,j])*x[i,j,kk] + Qk*(1-x[i,j,kk]), name=f"EV19_ub_...")
```

İstasyon düğümünde `YE[i] >= ye[i]` olsa bile (şarj gerçekleşse bile), `EV18_ub` (daha küçük olan `ye[i]`'ye dayalı) bağlayıcı kısıt olarak kalıyor ve `EV19_ub`'un (şarjı yansıtan, daha gevşek) sağladığı ek payı etkisiz kılıyor — **Faz 2'nin A1 olarak tanımladığı mimari kusurun aynısı.**

**Doğrulanmamış sonuç:** Eğer bu okuma doğruysa, mevcut `raw/EV_v.1.1.py`'de istasyonlarda şarj etmek, sonraki bacağın enerji bütçesine katkı sağlamıyor olabilir — yalnızca menzil içindeki (istasyona hiç uğramadan tamamlanabilecek) rotalar fizibıl kalır. Küçük problem örnekleri (C5/R5/RC5 gibi) muhtemelen şarj gerektirmediği için bu, "Değişiklik Raporu - v1.1.docx"ndeki başarılı test sonuçlarında (bkz. [[sources/2026-08-22-ev_v1_1_rewrite]]) yakalanmamış olabilir.

## Bulgu 2 — A7 (CV `h_c` sabiti) yeniden mi ortaya çıktı?

Faz 2'de (bkz. [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]) `h_c`'nin (mesafe başına yakıt tüketim oranı) XML'deki `EnergyConsumptionRate` niteliğinden okunması sağlanmıştı; öncesinde sabit `1.0` idi.

**Yeni `raw/xml_data_loader.py` (2026-08-22), `parse_vehicle_file()` fonksiyonunda araç niteliklerini şu alanlarla sınırlıyor** (satır ~146-153): `Type`, `MaxSpeed`, `Range`, `BatteryCapacity`, `SoC`, `MaximumLoadCapacityKg`. **`EnergyConsumptionRate` alanı hiç okunmuyor.** `prepare_cv_data_from_instance()` fonksiyonu (satır ~264-265) `h_c`'yi yine **sabit `1.0`** olarak döndürüyor:

```python
'h_c': 1.0,
'g_c': 1.0,
```

Bu, Faz 2'nin A7 düzeltmesinin (`src/xml_data_loader_fixed.py`'deki `EnergyConsumptionRate` okuma + araç-bazlı `h_c_v` sözlüğü) yeni `raw/xml_data_loader.py`'ye hiç yansımadığını gösteriyor — aynı sabit-oran sorunu, tam olarak Faz 2 öncesindeki haliyle geri gelmiş görünüyor.

## Neden önemli

İkisi de "Değişiklik Raporu - v1.1.docx"nin iddia ettiği (kk_name düzeltmesi, boş XML kontrolü, CV-27/EV-22 araç-ekip tekilliği gibi) somut, test edilmiş düzeltmelerle **aynı teslimatın parçası** olarak geldi — yani bu iki potansiyel regresyon, yeni kod tabanının genel güvenilirliğini sorgulatan bir bulgu. `raw/CV_model_gurobi_exact.py` ve `raw/EV_v.1.1.py` başlığındaki yorumlar bu dosyaların "v1 (x_ijvt, ham Big-M)" sürümünden türetildiğini belirtiyor — muhtemelen Faz 2'nin `src/` dallanması yerine, orijinal (Faz 2 öncesi) `raw/` kod tabanından bağımsız bir yeni dal olarak geliştirilmiş, bu da Faz 2 kazanımlarının (A1, A7) miras alınmamasını açıklıyor.

## Önerilen sonraki adım (uygulama kararı değil, sadece öneri)

`trsp-exact-model-mimari` bu iki bulguyu R5 (veya istasyon/şarj gerektiren küçük bir örnek) üzerinde uçtan uca çalıştırarak doğrulamalı: (a) EV modelinde istasyon SoC'sinin gerçekten bir sonraki bacağa yansıyıp yansımadığı, (b) CV modelinde menzilin `G[v]/1.0` (gerçekçi olmayan büyük) mü yoksa `G[v]/EnergyConsumptionRate` mi olduğu.

## Doğrulama Sonucu (2026-08-22, trsp-exact-model-mimari)

Her iki bulgu da **Gurobi 13.0.0 ile uçtan uca koşularak DOĞRULANDI** ve `raw/` içinde
doğrudan düzeltildi. Kütüphanecinin statik okuması her iki maddede de doğru çıktı; üstelik
A1'in yanında, **A1'i tamamen gölgeleyen daha ağır bir hata** (depo yaylarında döngüsel
infeasibility) bulundu.

### Bulgu 1 (A1) — DOĞRULANDI, düzeltildi

- EV-18, `raw/EV_v.1.1.py:380-393`'te artık `S_set = set(S)` üzerinden **istasyon
  düğümlerinden çıkan yaylarda yazılmıyor** (Faz 2'nin `src/EV_v_1_1_fixed.py:472-483`
  düzeltmesiyle aynı mantık, v1.1'in `kk`/`z_veh`/çoklu-sefer yapısı korunarak).
- **Gurobi kanıtı (keskin test, C5, Q=600 Wh'a düşürülmüş batarya, rota sabitlenmiş
  `0→1→5→8(istasyon)→4→0`):**
  - A1 kusuru yeniden üretildiğinde (istasyon çıkış yaylarında EV-18 geri eklendiğinde):
    **INFEASIBLE**, IIS = `{EV18_ub_1_5, EV18_ub_5_8, EV24_depo_sarj_ub_1,
    EV26_donus_enerjisi_4, EV27_musteride_sarj_yok_4, **A1BUG_EV18_ub_8_4**}` — yani
    istasyon çıkış yayındaki EV-18 kısıtı **birebir IIS'in içinde**.
  - Düzeltilmiş kodla: **FEASIBLE**, istasyon 8'de `ye=0.0 Wh → YE=337.2 Wh`
    (alınan şarj 337.2 Wh) ve bu enerji sonraki bacaklarda fiilen kullanılıyor
    (müşteri 4'e varış `ye=328.6 Wh` = tam olarak depoya dönüş için gereken miktar).
  - Serbest arama testinde de (aynı Q, rota sabitlenmeden): kusurlu modelde 300 s'de
    **0 çözüm**; düzeltilmiş modelde çözüm bulunuyor ve **optimal rota istasyondan
    geçiyor** (`0→1→5→8→4→0`, obj 8371.2).

### Bulgu 1'in yanında bulunan daha ağır hata — EV modeli HER rota için infeasible'dı

A1'den bağımsız olarak, EV-17/EV-18/EV-19 kısıtları **depo yaylarını da (i=0, j=0)**
kapsıyordu. `ye[0]` tek bir değişken olduğundan `0→…→0` kapalı turu boyunca zincir
`ye[0] ≤ ye[0] − h_e·(tur mesafesi)` biçimine indirgeniyor ve modeli **her rota için**
infeasible yapıyordu. Ayrıntı ve IIS kanıtı: [[sorun_ev_depo_yaylarinda_dongusel_infeasibility]].
Bu, "Değişiklik Raporu - v1.1.docx" §5.2'deki *"EV: 60 saniyelik kısa test süresinde
optimal bulunamadı (beklenen)"* ifadesinin gerçek nedenidir — beklenen bir yavaşlık
değil, yapısal infeasibility idi.

### Bulgu 2 (A7) — DOĞRULANDI, düzeltildi

- `raw/xml_data_loader.py:152-158`'de `EnergyConsumptionRate` ve `BatteryRechargingRate`
  nitelikleri geri eklendi; `prepare_cv_data_from_instance` artık `h_c`'yi
  (`raw/xml_data_loader.py:249-271, 293-294`) XML'den okuyor.
- **Git kanıtı:** `git diff raw/xml_data_loader.py` bu iki alanın v1.1 yeniden yazımında
  **silindiğini** gösteriyor (`- 'BatteryRechargingRate'`, `- 'EnergyConsumptionRate'`);
  yani bunlar önceki `raw/` sürümünde de vardı → net bir regresyondu.
- **Gurobi kanıtı (R5, CV modeli):**
  - `h_c = 1.0` (regresyon hâli): **INFEASIBLE**, 2.5 s'de kanıtlandı.
    Neden: `G = Range = 6000` ve `h_c = 1.0` menzili 6 km'ye indiriyor; R5'te depoya
    en uzak müşteri için gidiş-dönüş `2·d(0,j) = 6610 m > 6000` olduğundan
    CV-23/CV-24/CV-25 birlikte infeasibility üretiyor.
  - `h_c = 0.055` (XML değeri): **OPTIMAL, obj = 10116.1**, 1.8 s.
  - R7: `h_c=1.0` → 60 s'de çözüm yok; `h_c=0.055` → OPTIMAL 11150.9 (19.6 s).
  - Uçtan uca gerçek script koşumu (`python raw/CV_model_gurobi_exact.py`, girdi `R5`):
    OPTIMAL 10116.1, %0.00 gap.
- Etkilenen örnekler taraması (`2·max d(0,j) > 6000` → `h_c=1.0` ile infeasible):
  **R5, R7, R10, RC13, RC15**. C ailesi ve RC5/RC7/RC10 etkilenmiyor (bu yüzden C5
  testlerinde fark görünmüyordu — C5 her iki değerde de obj 8291.2 veriyor).

### Sonuç

Sayfanın "Önerilen sonraki adım" bölümündeki iki soru da yanıtlandı:
(a) istasyon SoC'si düzeltme öncesinde bir sonraki bacağa **yansımıyordu** (artık yansıyor),
(b) CV menzili `G/1.0 = 6000 m` idi, artık `G/0.055 ≈ 109 km`. `status` `taslak` → `güncel`
(çözüldü) olarak güncellendi.

## Sources

- `raw/EV_v.1.1.py:376-399` (EV18/EV19 — depo yayı ve istasyon istisnaları, düzeltilmiş hâl)
- `raw/EV_v.1.1.py:326-358` (EV17 — depo yayı istisnası + geçerli Big-M)
- `raw/EV_v.1.1.py:401-454` (yeni EV-24/25/26/27)
- `raw/xml_data_loader.py:152-158` (`EnergyConsumptionRate` geri eklendi)
- `raw/xml_data_loader.py:249-294` (`h_c` artık XML'den)
- `raw/EV_v.1.1.py:330-346` (EV18/EV19, istasyon istisnası yok — DÜZELTME ÖNCESİ hâl)
- `raw/xml_data_loader.py:146-153` (vehicle_attrs alanları, `EnergyConsumptionRate` yok)
- `raw/xml_data_loader.py:264-265` (`h_c: 1.0` sabiti)
- `src/EV_v_1_1_fixed.py:472-483` (A1 düzeltmesinin orijinal hâli — karşılaştırma için)
- `src/xml_data_loader_fixed.py:249-269,289` (A7 düzeltmesinin orijinal hâli — karşılaştırma için)

## Related

- [[sorun_ev_depo_yaylarinda_dongusel_infeasibility]]
- [[karar_ev_depo_sarj_ve_donus_enerjisi_kisitlari]]
- [[sorun_ev17_big_m_gecersiz_kucuk]]
- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
- [[degisken_yakit_enerji_izleme]]
- [[sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi]]
- [[sources/2026-08-22-ev_v1_1_rewrite]]
- [[sources/2026-08-22-xml_data_loader_v1_1]]
