---
title: Sorun — Operasyon Raporu Molayı 1 Saat Sayıyordu, Model 2 Saat (ll_k − el_k) Ayırıyor
tags: [sorun, raporlama, mola, cv, ev, v1.1, cozuldu]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py; raw/xml_data_loader.py
date: 2026-08-22
status: güncel
---

# Sorun — Rapordaki Mola Süresi ile Modeldeki Mola Süresi Uyuşmuyordu

## Kütüphanecinin "Bulgu 7" şüphesinin yanıtı

Şüphe: v1.1'de mola parametreleri artık sabit `break_duration/break_min/break_max`
yerine `xml_data_loader`'ın `el_val = 14400` / `ll_val = 21600` varsayılanlarından
geliyor; bu, mola penceresini ~20 dakikadan ~2 saate genişletiyor gibi görünüyor —
kasıtlı mı, bug mı?

**Yanıt: model tarafı KASITLI, rapor tarafı BUG.**

### Model tarafı kasıtlı (docx ile doğrulandı)

`yeni dosyalarım/Matematiksel_Model_rev_v1.1/Matematiksel Model - CV ve EV.docx`
mola parametrelerini `[el_k, ll_k]` = "k kaynağının öğle molası aralığı" olarak
tanımlıyor ve mola süresini kısıtlara **`w_ijk·(ll_k − el_k)`** terimiyle sokuyor
(CV-6, CV-8, EV-6, EV-7 denklemleri). Yani v1.1 matematiksel modelinde mola süresi,
ayrı bir `break_duration` parametresi değil, **mola penceresinin genişliğidir.**
Kod bunu birebir uyguluyor (`raw/CV_model_gurobi_exact.py:231-239`,
`raw/EV_v.1.1.py:232-240`). Docx ↔ kod **çelişkisi yok.**

Karşılaştırma için, v1 (`git show HEAD:raw/CV_model_gurobi_exact.py:70-72`) sabit
kodlanmış üç ayrı parametre kullanıyordu:
`break_duration = 3600`, `break_min = 13800` (11:50), `break_max = 15000` (12:10).
v1.1'de bu tasarım terk edilmiş, mola "pencere = süre" biçimine dönüşmüştür.
Mevcut veriyle pencere `[14400, 21600]` = 12:00–14:00 ⇒ **mola süresi 7200 s (2 saat).**
Bu değerlerin `xml_data_loader`'da sabit kodlanmış olması ayrı bir sorundur
(bkz. [[sorun_hardcoded_mola_parametreleri]]) ama bir kod↔model çelişkisi değildir.

### Rapor tarafı bug (düzeltildi)

`print_cv_solution` / `print_ev_solution` mola süresini **sabit 3600 s** varsayıyor ve
ekrana `"Yolda Öğle Molası (1 Saat) Kullanıldı"` yazıyordu. Üç yerde:
mola bitiş saati (`mola_bit = mola_bas + 3600`), depoya dönüş saati
(`end_val += 3600`) ve sefer süresi (`end_time += 3600`). Sonuç: model 2 saat
ayırırken rapor **dönüş saatlerini ve sefer sürelerini 1 saat erken** gösteriyordu.

Düzeltme (`raw/CV_model_gurobi_exact.py:496-498`, `raw/EV_v.1.1.py:529-531` ve bunları
kullanan üç nokta):

```python
break_start = float(data['el'][t])          # 14400  -> 12:00
break_end   = float(data['ll'][t])          # 21600  -> 14:00
break_dur   = break_end - break_start       # 7200 s = 2 saat
```

Ayrıca **molanın gösterilen saati de düzeltildi**: eski rapor molayı "hizmet biter
bitmez başlar" varsayıyordu (örn. `08:54 - 10:54`), oysa CV-10/EV-9 mola öncesi
hizmetin `el_k`'den **önce** bitmesini, CV-12/EV-11 mola sonrası düğüme `ll_k`'den
**sonra** varılmasını zorunlu kılar — yani mola fiilen `[el_k, ll_k]` penceresini
işgal eder. Rapor artık `[ 12:00 - 14:00 ]` yazıyor. Mola son bacakta kullanıldığında
depoya dönüş saati de `ll_k + tt(son_müşteri, 0)` olarak (modelin dayattığı değer)
hesaplanıyor.

**Düzeltme sonrası örnek çıktı (EV, C5):**

```
[ 11:35 ] ➔ Müşteriye Varış. Nokta: 5   ↳ Ayrılış Saati: 12:00
☕ [ 12:00 - 14:00 ] Yolda Öğle Molası (2 Saat) Kullanıldı.
[ 14:00 ] ➔ Müşteriye Varış. Nokta: 4
...
[ 14:02 ] 🏁 Depoya Dönüş sağlandı.      (= ll_k + tt = 14:00 + 2 dk)
```

## Sources

- `yeni dosyalarım/Matematiksel_Model_rev_v1.1/Matematiksel Model - CV ve EV.docx` (CV-6/CV-8/EV-6/EV-7 denklemleri, `w_ijk(ll_k − el_k)`; parametre listesi "öğle molası aralığı")
- `raw/CV_model_gurobi_exact.py:224-239` (CV-8, mola teriminin modeldeki hâli)
- `raw/CV_model_gurobi_exact.py:496-498` (`break_dur` düzeltmesi)
- `raw/EV_v.1.1.py:529-531` (aynı düzeltme, EV)
- `raw/xml_data_loader.py:226-227, 309-310` (`el_val = 14400`, `ll_val = 21600` varsayılanları)
- v1 karşılaştırması: `git show HEAD:raw/CV_model_gurobi_exact.py` satır 70-72

## Related

- [[sorun_hardcoded_mola_parametreleri]]
- [[parametre_mola_zaman_sabitleri]]
- [[celiski_ogle_molasi_zorunlulugu]]
- [[cozum_raporlama_fonksiyonlari]]
