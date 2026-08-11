---
title: EV Model Çalıştırma Parametreleri (Modül Seviyesi Bayraklar)
tags: [entity, parametre, ev, gurobi-tuning, konfigürasyon]
source: raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# EV Model Çalıştırma Parametreleri

`EV_v.1.1.py` dosyasının başında (satır 16-24) tanımlı, `CV_model_gurobi_exact.py`'de karşılığı olmayan 5 modül-seviyesi bayrak:

| Parametre | Değer | Anlamı |
|---|---|---|
| `ENABLE_PAIR_CREWS` | `True` | İkili teknisyen ekipleri (`itertools.combinations`) oluşturulsun mu |
| `FEASIBILITY_FOCUSED_PARAMS` | `True` | Aşağıdaki Gurobi tuning parametreleri uygulansın mı — bkz. [[karar_ev_feasibility_gurobi_tuning_ve_diagnostik]] |
| `MAX_ROUTES_PER_VEHICLE` | `1` | Araç başına günlük en fazla rota sayısı (tek sefer) |
| `MODEL_TIME_LIMIT_SECONDS` | `3600` (1 saat) | Gurobi zaman sınırı — CV'nin 900 saniyelik (15 dk) sınırından çok daha yüksek |
| `TARGET_INSTANCE_SEQUENCE` | `["R15", "RC15", "RC13"]` | Varsayılan olarak sadece bu 3 problem örneği çalıştırılıyor |

`FEASIBILITY_FOCUSED_PARAMS=True` olduğunda ayarlanan Gurobi parametreleri (satır 741-755): `MIPFocus=2`, `Heuristics=0.15`, `NoRelHeurTime=600`, `NoRelHeurSolutions=5`, `RINS=25`, `SubMIPNodes=500`, `Presolve=2`, `Symmetry=2`, `MIPSepCuts=2`, `Cuts=2`, `IntegralityFocus=1`, `NumericFocus=1`, `MIPGap=0.005`.

## Neden önemli

EV modelinin CV'ye göre 4x daha uzun zaman sınırına (3600s vs 900s) ve 12 ek Gurobi tuning parametresine sahip olması, EV probleminin CV'ye göre çözücü için gözle görülür biçimde daha zor olduğunu gösteriyor — bu, [[sorun_ev_enerji_tuketim_modeli_basitlestirilmis]] ve [[sorun_kismi_sarj_dinamikleri_kodda_yok]]'ta tanımlanan yapısal karmaşıklıkla (istasyon, şarj, teknisyen çakışma önleme) tutarlı.

## Güncelleme (Faz 2, 2026-08-11) — `resolve_data_root()`

`src/EV_v_1_1_fixed.py:64-71` (aynı desen `src/CV_model_gurobi_fixed.py:548-...`'de de var) yeni bir yardımcı fonksiyon:

```python
def resolve_data_root() -> str:
    """Veri (XML) kokunu bul. src/ altinda veri yoksa salt-okunur raw/ kullanilir."""
    if os.path.isdir(os.path.join(SRC_ROOT, "trsp_problem_sets")):
        return SRC_ROOT
    candidate = os.path.join(os.path.dirname(SRC_ROOT), "raw")
    if os.path.isdir(os.path.join(candidate, "trsp_problem_sets")):
        return candidate
    return SRC_ROOT
```

**Neden gerekti:** `raw/EV_v.1.1.py`'nin orijinal veri/çıktı yolu deseni `os.path.dirname(__file__)`'e dayanıyordu — dosya `raw/` içindeyken bu, veri klasörlerini (`trsp_problem_sets/` vb.) doğrudan yanında buluyordu. Dosyalar `src/`'e taşınınca (bkz. [[karar_src_klasoru_ve_raw_izolasyonu]]) bu desen kırılırdı: `src/` içinde veri klasörleri yok, hâlâ `raw/`'dan okunmaları gerekiyor (Hard Rule 1 — `raw/`'a yazılmıyor ama okunuyor), çıktı ise yeni `src/sonuclar/` klasörüne yazılmalı. `resolve_data_root()` önce `src/` altında veri arıyor, bulamazsa `raw/`'a düşüyor — böylece hem eski hem yeni konumdan çalıştırma desteklenmiş oluyor.

## Sources

- `raw/EV_v.1.1.py:16-24,741-755`
- `src/EV_v_1_1_fixed.py:61-71,749`
- `src/CV_model_gurobi_fixed.py:548,582`

## Related

- [[karar_ev_feasibility_gurobi_tuning_ve_diagnostik]]
- [[gurobi_mip_cozucusu]]
- [[degisken_route_start_route_end_ev]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
