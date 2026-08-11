---
title: Karar (Faz 2, A1) — EV Şarj c20/c21 Çakışması Düzeltmesi
tags: [karar, faz2, ev, şarj-modeli, bug-fix, a1]
source: src/EV_v_1_1_fixed.py
date: 2026-08-11
status: güncel
---

# Karar (Faz 2, A1) — EV Şarj c20/c21 Çakışması Düzeltmesi

## Sorun

`raw/EV_v.1.1.py`'de `c20` (varış enerjisi zinciri) istasyon çıkış yaylarında da yazılıyordu. İstasyon düğümlerinde `YE[s] >= ye[s]` (dolum, `c22_station_recharge_lb`) her zaman geçerli olduğundan, `c20`'nin ürettiği sınır `c21`'in (gerçek şarj sonrası enerjiyi yansıtması gereken kısıt) etkisini her zaman eziyordu. Sonuç: `ye`/`YE` matematiksel olarak tanımlı ve `charge_time_i` zaman eksenine yansısa da, **şarj edilen enerji miktarı bir sonraki arc'ın tüketim hesabına hiçbir zaman gerçek biçimde girmiyordu** — model şarjı "yapmış gibi" davranıp içeriğini kullanmıyordu.

## Karar

`src/EV_v_1_1_fixed.py:472-531`'deki `c20` döngüsüne bir koşul eklendi:

```python
for i in ...:
    if i in S_set:
        continue  # A1: istasyon cikis yaylarinda c20 devre disi
    m.addConstr(ye[j, k] >= 0, name=f"c20_lb_{i}_{j}_{k}")
    ...
```

(Tam bağlam `src/EV_v_1_1_fixed.py:472-488`.) Böylece istasyon düğümlerinden çıkan arc'larda yalnızca `c21` (gerçek şarj sonrası enerjiden başlayan tüketim zinciri) etkili oluyor, `c20` bu düğümlerde devre dışı bırakılıyor.

## Doğrulama

- **Öncesi:** R5 problem setinde 0 çözüm (Gurobi `TIME_LIMIT` ile sonlandı, feasible çözüm bulunamadı).
- **Sonrası:** Aynı problem setinde 8 çözüm bulundu, `obj=10118.32`.
- İstasyon SoC örneği: bir istasyonda `ye`=751.54 iken `YE`=1000.00 (tam dolum) — düzeltme öncesi bu artış bir sonraki arc'ın tüketim hesabına yansımıyordu, sonrasında yansıyor.
- `c20_ub` kısıtı istasyon çıkışında artık **0 adet** üretiliyor (önceden bu düğümlerde de üretiliyordu).

## Etki ve kalan iş

Bu düzeltme [[karar_partial_charging_denklemleri_entegrasyonu_plani]]'nın "kısmi şarj etkisiz" alt-sorununu giderdi, ama planın asıl hedefi olan Keskin & Çatay (2016) tam eşitlik denklemleri hâlâ yok. `ye`/`YE` hâlâ sadece `<=` eşitsizliklerle bağlı (eşitlik değil) — bu, yeni bir raporlama sorununa yol açtı, bkz. [[sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi]].

## Sources

- `src/EV_v_1_1_fixed.py:472-531`
- `raw/EV_v.1.1.py:306-353` (orijinal, hatalı davranışın kaynağı)

## Related

- [[karar_partial_charging_denklemleri_entegrasyonu_plani]]
- [[sorun_ye_ye_esitsizlik_kismi_sarj_raporlama_hatasi]]
- [[sorun_sarj_yakit_istasyonlari_kodda_yok]]
- [[degisken_yakit_enerji_izleme]]
- [[partial_recharging]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
