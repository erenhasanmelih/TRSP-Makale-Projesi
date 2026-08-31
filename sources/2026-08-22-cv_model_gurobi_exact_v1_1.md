---
title: CV_model_gurobi_exact.py (v1.1) — CV Exact MIP Modeli, Yeniden Yazım
tags: [kaynak, kod, cv, gurobi, mip, v1.1]
source: raw/CV_model_gurobi_exact.py
date: 2026-08-22
status: güncel
---

# CV_model_gurobi_exact.py (v1.1) — CV Exact MIP Modeli, Yeniden Yazım

## Amaç

Bu, `raw/CV_model_gurobi_exact.py`'nin 2026-08-22'de Eren'in onayıyla tamamen değiştirilen içeriğinin analizidir (791 satır fark, 456→765 satır). Önceki içerik `2026-08-09-cv_model_gurobi_exact (silindi)` sayfasında belgelenmiştir (silindi). Bu sayfa **güncel `raw/` durumunu** yansıtır.

## Ne değişti (v1.0 → v1.1)

Dosya başındaki yorum, bu sürümün "hasan taslak makale 1.docx, Bölüm 3.4.1" ile birebir eşleştiğini ve önceki 4-boyutlu (`x[i,j,v,t]`, ham Big-M) sürümün ayrı bir yedek dosyada ("CV_model_gurobi_exact - yedek (v1, x_ijvt).py") saklandığını belirtiyor.

### Yapısal değişiklikler

- **İndis düşürme:** `x[i,j,v,t]` (4B) → `x[i,j,kk]` (3B), `kk = (v,t)`, `K = [(v,t) for v in V for t in T]` (satır 54). Faz 2'nin (`src/CV_model_gurobi_fixed.py`) `K_pairs`/`KK` yaklaşımıyla kavramsal olarak aynı ama **bağımsız bir uygulama** — burada `kk` doğrudan tuple, tamsayı indeks yok.
- **`kk_name` temiz isimlendirme** (satır 56-74): `.lp` yazımını kıran ham Python tuple string sorununu çözüyor — bkz. [[kk_name_degisken_temiz_isimlendirme]].
- **Tight Big-M — artık `raw/`'da da var:** sabit `100000.0` YOK; her Big-M ifadesi zaman penceresi/mesai parametrelerinden türetiliyor (örn. CV6: `bigM = a_max + ls[t_] + (ll[t_]-el[t_])`, CV14: `bigM = ls[t_] - ll[t_]`). Bkz. [[parametre_big_m_100000]] güncellemesi.
- **Çoklu sefer gerçekten var (CV-4, satır 143-152):** `<= 3*z[kk]` — bkz. [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]].
- **`z` değişkeni + CV-27/CV-28 (satır 100-184):** araç-ekip ve teknisyen tekilliği, `solution_validator.py`'de bulunan gerçek bir hatayı önlüyor.
- **Kaldırılan ölü değişkenler:** `L[i,t]` ve `alpha[Fc,Vc]` artık **hiç tanımlanmıyor** (önceki sürümde tanımlı ama kullanılmıyordu).
- **CV-26 denenip geri alınmış** (satır 398-414): depodan ilk çıkış zaman ilerlemesi kısıtı, `tau[0,k]`'nin hem çıkış hem dönüş anlamı taşımasının döngüsel çelişkiye yol açtığı görülüp kaldırılmış; çözüm rapor katmanına taşınmış (çıkış saati geriye doğru türetiliyor).

### `build_model()` imzası (satır 23-29)

```python
def build_model(N, N0, C, Vc, V, T, Ti, Fc, A, d, tt, st, G, ec, lc, es, ls, el, ll,
                 h_c, g_c, k, lc0, a_max=None, node_labels=None, crew_members=None):
```

Önceki sürümle aynı pozisyonel parametre listesi + iki yeni opsiyonel parametre (`a_max`, `crew_members`). `crew_members` verilmezse her ekip atomik teknisyen kabul ediliyor (CV-28'in ön koşulu).

### Kısıt envanteri (CV-1 … CV-25, + CV-27/28)

Amaç (CV-1) → atama (CV-2) → tekil arc (CV-3) → çoklu sefer+z (CV-4/27/28) → akış (CV-5) → istasyon zaman ilerlemesi (CV-6/7/11, `real_stations = [s for s in Fc if s!=0]` ile filtreli — hâlâ boş liste, veri setinde gerçek istasyon yok) → müşteri zaman ilerlemesi (CV-8) → mola onayı/sonrası/öncesi (CV-9/10/12) → opsiyonel mola (CV-13, `<=`) → molasız erken dönüş (CV-14) → mesai sınırları (CV-15/16/17) → zaman penceresi (CV-18) → yakıt zaman ilerlemesi (CV-19) → yakıt tüketimi (CV-20/21) → ayrılış=varış no-refuel (CV-22) → depoda tam dolum (CV-23/24) → dönüş yakıtı garantisi (CV-25).

### `__main__` akışı — yeni düzeltmeler

- `os.path.getsize(employee_file) > 0` kontrolü eklendi (satır 629) — boş `Info4Employee.xml` çökmesini önlüyor (bkz. "Değişiklik Raporu - v1.1.docx", madde 2.1).
- `.lp` yazımı artık `try/except gp.GurobiError` ile sarılı (satır 740-744) — Türkçe karakterli mutlak yol hatası artık optimizasyonu durdurmuyor.
- `data['lc0'] = 40000.0` (satır 659) — `lc0` artık CV-19'da fiilen kullanılıyor (bkz. [[sorun_cv_kullanilmayan_istasyon_parametreleri]] güncellemesi).

## Regresyon riski (doğrulanmadı)

`xml_data_loader.py`'den gelen `h_c` hâlâ sabit `1.0` — bkz. [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]] (bu sayfa kasıtlı olarak `status: taslak`, dokunulmadı).

## Sources

- `raw/CV_model_gurobi_exact.py` (tam dosya, 765 satır, 2026-08-22)
- `yeni dosyalarım/Codes_rev_v1.1/Ana_Kodlar_ve_Açıklamaları.docx`
- `yeni dosyalarım/Matematiksel_Model_rev_v1.1/Matematiksel Model - CV ve EV.docx` (Bölüm 3.4.1)
- `yeni dosyalarım/Matematiksel_Model_rev_v1.1/Değişiklik Raporu - v1.1.docx`

## Related

- [[sources/2026-08-22-ev_v1_1_rewrite]]
- [[sources/2026-08-22-xml_data_loader_v1_1]]
- [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
- [[celiski_single_trip_vs_multitrip]]
- [[celiski_ogle_molasi_zorunlulugu]]
- [[kk_name_degisken_temiz_isimlendirme]]
