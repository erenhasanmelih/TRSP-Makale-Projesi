---
title: Parametre — Mola Zaman Sabitleri (break_duration, break_min, break_max)
tags: [entity, parametre, mola, hardcoded]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Parametre — Mola Zaman Sabitleri

Her iki dosyada birebir aynı üç sabit (CV: satır 70-72, EV: satır 156-158):

```python
break_duration = 3600   # Tam 1 Saat
break_min = 13800       # 11:50 (+10/-10 dk tolerans alt sınırı)
break_max = 15000       # 12:10 (+10/-10 dk tolerans üst sınırı)
```

`format_time()`'daki `+28800` kaymasıyla birlikte yorumlandığında: model saniyesi `13800` → gerçek saat `13800+28800=42600s = 11:50`; `15000` → `43800s = 12:10`. Bu nedenle yorum satırındaki saatler doğru.

Bu sabitler [[sorun_hardcoded_mola_parametreleri]]'nde tanımlanan sorunun doğrudan kod kanıtıdır — model tarafında parametrik olması beklenirken kodda sabit.

## Sources

- `raw/CV_model_gurobi_exact.py:70-72`
- `raw/EV_v.1.1.py:156-158`

## Related

- [[sorun_hardcoded_mola_parametreleri]]
- [[karar_operasyonel_zaman_kaydirma_format_time]]
- [[celiski_ogle_molasi_zorunlulugu]]
