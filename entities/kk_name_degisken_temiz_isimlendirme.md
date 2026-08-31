---
title: kk_name — Gurobi Değişken/Kısıt İsimlerinin Temizlenmesi
tags: [entity, fonksiyon, gurobi, bug-fix, isimlendirme, v1.1]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-22
status: güncel
---

# kk_name — Gurobi Değişken/Kısıt İsimlerinin Temizlenmesi

## Sorun

`k = (v, t)` (araç, ekip) birleşik indeksi bir Python tuple'ıdır. Gurobi'nin `addVars()` ile otomatik ürettiği değişken isimleri, tuple indeksleri ham Python `str()` hâliyle kullanır (örn. `x[0,1,('EV_1', 'TECH_008')]` — boşluk, tırnak, parantez içerir). "Değişiklik Raporu - v1.1.docx" (madde 2.3), bunun `.lp` dosyası formatında **geçersiz/riskli isimler** ürettiğini ve Gurobi'nin bu konuda ayrıca uyarı verdiğini belirtiyor.

## Çözüm

Her iki dosyada da (`CV_model_gurobi_exact.py:56-74`, `EV_v.1.1.py:73-86`) birebir aynı desen:

```python
kk_name = {kk: f"{kk[0]}_{kk[1]}" for kk in K}   # örn. "EV_1_TECH_008"

def _clean_part(p):
    return kk_name[p] if isinstance(p, tuple) else str(p)

def _rename(var_dict, prefix):
    for key, var in var_dict.items():
        parts = key if isinstance(key, tuple) else (key,)
        var.VarName = f"{prefix}[{','.join(_clean_part(p) for p in parts)}]"
```

`_rename()`, her karar değişkeni grubuna (`x`, `tau`, `w`, `Delta_c`/`Delta_s`, `z`/`z_veh`, ...) uygulanıyor — hem model kurulumundan hemen sonra hem de `.lp` yazımından önce.

## Neden önemli

Bu, salt kozmetik bir düzeltme değil — düzeltilmeden önce `.lp` dosyası yazımı `"Unable to write to file"` hatasıyla çöküyordu (bu, ["Değişiklik Raporu"](../yeni%20dosyalar%C4%B1m) belgesindeki 3 hatadan biri, madde 2.2 ile birlikte). `kk_name` sözlüğü aynı zamanda kısıt adlarında da kullanılıyor (`f"CV4_multitrip_{kk_name[kk]}"` gibi) — bu da Gurobi log/IIS çıktısının okunabilirliğini artırıyor.

## Sources

- `raw/CV_model_gurobi_exact.py:56-74,110-114`
- `raw/EV_v.1.1.py:73-86,126-134`
- `yeni dosyalarım/Matematiksel_Model_rev_v1.1/Değişiklik Raporu - v1.1.docx` (madde 2.2-2.3)

## Related

- [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]]
- [[sources/2026-08-22-ev_v1_1_rewrite]]
- [[degisken_x_arc_tahsisi]]
- [[degisken_z_arac_ekip_atama]]
