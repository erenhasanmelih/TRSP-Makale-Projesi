---
title: Karar (v1.1) — Gerçek Çoklu Sefer + z Değişkenli Araç-Ekip/Teknisyen Tekilliği (CV-27/28, EV-22/23)
tags: [karar, v1.1, coklu-sefer, tekillik, solution_validator, cv, ev]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py; raw/solution_validator.py
date: 2026-08-22
status: güncel
---

# Karar (v1.1) — Gerçek Çoklu Sefer + z Değişkenli Araç-Ekip/Teknisyen Tekilliği

## Ne değişti

`raw/CV_model_gurobi_exact.py` ve `raw/EV_v.1.1.py`'nin 2026-08-22 tarihli yeniden yazımı, önceki (Faz 1/Stage 2'de doğrulanmış) **tek-sefer** davranışını terk edip her iki modelde de **günde en fazla 3 sefer** (çoklu sefer) kısıtını gerçekten uyguluyor — ve bunu, `solution_validator.py` ile bulunan gerçek bir hatayı önleyen yeni bir `z` (araç-ekip atama) değişkeniyle birlikte yapıyor.

### 1. Çoklu sefer (CV-4 / EV-4, ≤3)

```python
# CV: CV_model_gurobi_exact.py:148-152
for kk in K:
    m.addConstr(gp.quicksum(x[0, j, kk] for j in N0 if (0, j) in A) <= 3 * z[kk], name=f"CV4_multitrip_{kk_name[kk]}")

# EV: EV_v.1.1.py:169-173 (aynı yapı, z_veh)
```

Bu, [[celiski_single_trip_vs_multitrip]]'te uzun süredir çözülmemiş kalan docx↔kod çelişkisini fiilen kapatıyor — bkz. o sayfadaki "ÇÖZÜLDÜ (2026-08-22)" güncellemesi.

### 2. z değişkeni — araç-ekip tekilliği (CV-27 / EV-22)

`solution_validator.py` ile test sırasında bulunan gerçek bir hata: hiçbir kısıt yokken Gurobi, aynı fiziksel aracı (`CV_3` örneği, RC7 problem setinde) **iki farklı ekiple, çakışan saatlerde** kullanabiliyordu — fiziksel olarak imkânsız. Düzeltme, her aracın günde en fazla bir ekibe atanmasını zorunlu kılan ikili bir `z[v,t]` değişkeni:

```python
z = m.addVars(K, vtype=GRB.BINARY, name="z")   # CV; EV'de z_veh
for v in V:
    m.addConstr(gp.quicksum(z[v, t] for t in T) <= 1, name=f"CV27_arac_ekip_tekillik_{v}")
```

Çoklu sefer kısıtı (CV-4/EV-4) bu değişkene bağlı: `z[kk]=0` olduğunda o kaynak (araç,ekip) hiç depodan çıkamıyor.

### 3. Teknisyen tekilliği (CV-28 / EV-23)

CV-27/EV-22 tek başına yetersiz: `T` kümesi hem bireysel (`"TECH_001"`) hem ikili (`"TECH_001_TECH_007"`) ekip kimliklerini ayrı kaynaklar olarak içerdiğinden, aynı ham teknisyen aynı gün hem tek başına bir araçta hem bir ikilinin parçası olarak başka bir araçta "atanmış" görünebilirdi. `crew_members` haritası üzerinden her ham teknisyenin toplam aktif atamasını 1 ile sınırlayan ek bir kısıt eklendi:

```python
for tech in all_raw_techs:
    m.addConstr(gp.quicksum(z[v, t] for v in V for t in T if tech in crew_members.get(t, {t})) <= 1,
                name=f"CV28_teknisyen_tekillik_{tech}")
```

## Bilinen sınır (kodun kendi yorumunda dürüstçe belirtilmiş)

CV-27/28 ve EV-22/23, **farklı** kaynaklar arasındaki çakışmayı engelliyor. **Aynı** kaynağın (örn. `CV_1` + `TECH_001` ekibi) kendi 2. ve 3. seferlerinin **kronolojik sırası** ayrıca zorlanmıyor — bir kısıt denenmiş (CV-26/EV-21, "depodan ilk çıkış zaman ilerlemesi") ama `tau[0,k]`'nin hem çıkış hem dönüş zamanı olarak kullanılmasının döngüsel çelişki (infeasibility) yarattığı görülüp geri alınmış (bkz. `CV_model_gurobi_exact.py:398-414` içindeki ayrıntılı yorum). Kod, bunun "riskli olmadığını" çünkü amaç fonksiyonunun (toplam mesafe) `tau` sırasına değil seçilen arc'lara bağlı olduğunu belirtiyor; her çözümden sonra bu varsayımı sayısal olarak denetleyen mekanizma `raw/solution_validator.py`'dir (bkz. [[solution_validator_fonksiyonlari]]).

### GÜNCELLEME (2026-08-23) — bu sınır KAPATILDI

Yukarıdaki "bilinen sınır" 2026-08-23'te giderildi:
[[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] uygulandı ve CV-4 tek
kısıttan **CV-4a/b/c/d** dörtlüsüne (yeni `u[r,k]` değişkeniyle) ayrıştırıldı
(`raw/CV_model_gurobi_exact.py:212-243`, `raw/EV_v.1.1.py:224-254`). CV-29/EV-28
artık aynı kaynağın kendi seferleri arasındaki kronolojik sırayı **model
düzeyinde** garanti ediyor. `z[v,t]` / `z_veh[v,t]` yapısı, CV-27/28 ve
EV-22/23 kısıtları **hiç değişmedi** — klonlama düğüm ekseninde yapıldı, kaynak
ekseninde değil. Ayrıntı ve sayısal kanıt:
[[sorun_coklu_sefer_zaman_sirasi_ihlali]] "ÇÖZÜLDÜ (2026-08-23)".

## Eski EV mekanizmasının yerini alması

Eski `raw/EV_v.1.1.py`'de bu sorunun bir alt kümesini (yalnızca "aynı teknisyen iki ekipte, çakışan saatlerde" durumunu, zaman-penceresi tabanlı `route_start`/`route_end`/`ord_*` ile) çözen çok daha karmaşık bir mekanizma vardı (bkz. degisken_route_start_route_end_ev (silindi) — artık `raw/`'da yok). Yeni `z`-tabanlı yaklaşım hem daha basit hem daha genel (araç VE teknisyen düzeyinde, zaman penceresi hesabı gerektirmeden) ama farklı bir boşluğu (aynı kaynağın kendi seferleri arası sıralama) miras bırakıyor — eski mekanizma da zaten bunu çözmüyordu, bu yeni bir gerileme değil.

## Sources

- `raw/CV_model_gurobi_exact.py:100-184` (z, CV4, CV27, CV28)
- `raw/EV_v.1.1.py:120-195` (z_veh, EV4, EV22, EV23)
- `raw/CV_model_gurobi_exact.py:398-414` (CV-26 geri alınma notu)
- `raw/solution_validator.py` (doğrulayıcı, tam kaynak)
- `yeni dosyalarım/Matematiksel_Model_rev_v1.1/Değişiklik Raporu - v1.1.docx` (RC7'de CV_3 örneği, "3. Ayrıca Bu Turda Eklenen İyileştirme")
- `yeni dosyalarım/Matematiksel_Model_rev_v1.1/Matematiksel Model - CV ve EV.docx` (CV-27/28, EV-22/23 resmi tanımları)

## Related

- [[celiski_single_trip_vs_multitrip]]
- [[solution_validator_fonksiyonlari]]
- [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]]
- [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]]
- [[sources/2026-08-22-ev_v1_1_rewrite]]
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]
