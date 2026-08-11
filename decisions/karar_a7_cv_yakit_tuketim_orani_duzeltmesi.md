---
title: Karar (Faz 2, A7) — CV Yakıt Tüketim Oranı Düzeltmesi
tags: [karar, faz2, cv, yakıt-modeli, bug-fix, a7, heterojen-filo]
source: src/xml_data_loader_fixed.py
date: 2026-08-11
status: güncel
---

# Karar (Faz 2, A7) — CV Yakıt Tüketim Oranı Düzeltmesi

## Sorun

`raw/CV_model_gurobi_exact.py`'nin veri hazırlama akışında `h_c` (mesafe başına yakıt tüketim katsayısı) `1.0` sabitine düşüyordu; XML kaynak dosyasındaki `EnergyConsumptionRate` niteliği **hiç okunmuyordu**. Bu, CV aracının menzilini gerçekçi olmayan biçimde büyütüyordu: `G[v]/h_c = 6000/1.0 = 6000` metre — oysa gerçek `EnergyConsumptionRate` değeriyle (`0.055`) menzil `6000/0.055 ≈ 109091` metre olmalıydı.

## Karar

`src/xml_data_loader_fixed.py:249-269,289`'da CV veri hazırlama fonksiyonu, aracın `EnergyConsumptionRate` niteliğini XML'den (`FC_Info4Vehicle4CV.xml`, örnek değer `"0.055"`) okuyacak şekilde düzeltildi:

```python
h_c = float(vehicle_attrs.get(ref_v, {}).get('EnergyConsumptionRate', 0.0)) if ref_v else 0.0
...
h_c_v = {}
for v in ...:
    rate = float(vehicle_attrs.get(v, {}).get('EnergyConsumptionRate', 0.0) or 0.0)
    h_c_v[v] = rate if rate > 0.0 else h_c
```

Ayrıca **araç-bazlı** `h_c_v` (CV) ve `h_e_v` (EV) sözlükleri eklendi — böylece filo homojen değilse (farklı araçların farklı tüketim oranları varsa) her araç kendi gerçek oranıyla modellenir. Bu, [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]'deki `he_of_k[k]`/`hc_of_k[k]` çok-indisli yapılarının veri kaynağıdır.

## Doğrulama

- Düzeltme sonrası CV menzili: `6000/0.055 ≈ 109091` metre — EV'nin menziliyle (`322580` metre, `h_e`'ye bağlı) artık aynı büyüklük mertebesinde (öncesinde CV menzili `6000` metre gibi gerçekçi olmayan biçimde küçüktü/hatalı ölçekliydi).
- R5 problem setinde Gurobi 13 ile OPTIMAL çözüm alındı, CV `obj=10116.10` — EV ile tutarlı (aynı) objektif değeri.

## Sources

- `src/xml_data_loader_fixed.py:249-269,289,346-353,380`
- `raw/xml_data_loader.py` (orijinal, `EnergyConsumptionRate` okunmuyor)
- `raw/CV_model_gurobi_exact.py` (h_c=1.0 sabitinin tüketildiği yer)

## Related

- [[sorun_ev_enerji_tuketim_modeli_basitlestirilmis]]
- [[sorun_cv_kullanilmayan_istasyon_parametreleri]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]
- [[degisken_yakit_enerji_izleme]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
