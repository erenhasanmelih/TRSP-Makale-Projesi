---
title: Sorun (Faz 2, Küçük) — tau_ub İstasyon/Depo Ufuk Sapması
tags: [sorun, faz2, big-m, tau_ub, ürün-kararı-bekliyor]
source: src/EV_v_1_1_fixed.py; src/CV_model_gurobi_fixed.py
date: 2026-08-11
status: güncel
---

# Sorun (Faz 2, Küçük) — tau_ub İstasyon/Depo Ufuk Sapması

## Sorun

`raw/`'daki yükleyicide istasyon/depo düğümleri için yapay bir "büyük sayı" (`lc=100000`, gerçek bir zaman penceresi üst sınırı değil) kullanılıyordu. Faz 2'de bu, `tau_ub[i] = horizon_end` (vardiya ufku, `ls` değerlerinin maksimumu veya müşteri `lc` değerlerinin maksimumu) ile değiştirildi:

```python
horizon_end = max([float(vv) for vv in ls.values()]) if ls else 32400.0
...
tau_ub = {}
for i in ...:
    if i is müşteri:
        tau_ub[i] = min(float(lc[i]), horizon_end)
    else:  # istasyon/depo
        tau_ub[i] = horizon_end
```

(EV: `src/EV_v_1_1_fixed.py:159-173`, CV: `src/CV_model_gurobi_fixed.py:78-91`.)

## Etkisi

Bu, **"vardiya bitiminden sonra istasyon/depo ziyareti olamaz"** anlamına gelen hafif bir sıkılaştırmadır. Orijinal modelde (yapay `lc=100000` ile) bu sınır fiilen yok gibiydi (pratik olarak sonsuza yakın); Faz 2'de gerçek bir ufuk sınırı getirildi.

## Neden not edildi

Bu, herhangi bir yönerge belgesinde açıkça talep edilmiş bir kural değil — Faz 2'nin C2 (tight Big-M) çalışması sırasında M değerlerini türetmek için `tau_ub[i]`'nin **anlamlı bir sonlu değer** olması gerektiğinden ortaya çıkan bir yan karar. `100000.0` gibi yapay bir sayı üzerinden M türetmek, M'yi de yapay olarak büyütürdü — bu yüzden istasyon/depo düğümlerine de gerçek bir ufuk sınırı verildi.

## Geri alınabilirlik

Karar geri alınabilir: `tau_ub[i] = lc[i]` (orijinal yapay değer) yapılırsa eski davranışa dönülür, ama bu durumda ilgili Big-M'ler (bkz. [[karar_c2_tight_big_m_uygulamasi]]) gevşer — yani tight-M kazanımının bir kısmı bu kararla bağlantılı.

## Durum

**Ürün kararı bekliyor.** Bu sıkılaştırmanın kabul edilebilir bir varsayım mı yoksa modelin orijinal davranışından (kısıtsız istasyon/depo ufku) bilinçli bir sapma mı olduğu Eren tarafından onaylanmalı.

## Sources

- `src/EV_v_1_1_fixed.py:159-173`
- `src/CV_model_gurobi_fixed.py:78-91`
- `raw/EV_v.1.1.py` (orijinal, `lc=100000` yapay değer)
- `raw/CV_model_gurobi_exact.py` (orijinal, `lc=100000` yapay değer)

## Related

- [[karar_c2_tight_big_m_uygulamasi]]
- [[karar_a4_zaman_penceresi_bigm_kosullandirma]]
- [[tight_big_m]]
- [[parametre_big_m_100000]]
