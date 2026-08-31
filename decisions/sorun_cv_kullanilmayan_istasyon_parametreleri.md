---
title: Sorun (Kod, CV) — Kullanılmayan İstasyon-İlişkili Parametreler (Fc, alpha, g_c, k, lc0)
tags: [sorun, kod, cv, ölü-kod, istasyon]
source: raw/CV_model_gurobi_exact.py
date: 2026-08-09
status: güncel
---

# Sorun (Kod, CV) — Kullanılmayan İstasyon-İlişkili Parametreler

## Sorun

`CV_model_gurobi_exact.py:13-16`'daki `build_model()` fonksiyonuna geçirilen şu parametreler, fonksiyon gövdesinde (satır 18-197) **hiçbir kısıtta veya ifadede kullanılmıyor**:

- `Fc` — sadece kullanılmayan `alpha = m.addVars(Fc, Vc, ...)` değişkenini (satır 27) boyutlandırmak için var; `alpha` değişkeninin kendisi de hiçbir kısıtta geçmiyor.
- `g_c` — CV'deki EV'nin `g_e` (şarj süresi katsayısı) karşılığı olması muhtemel, ama hiç kullanılmıyor.
- `k` — amacı belirsiz, hiç kullanılmıyor.
- `lc0` — `__main__` bloğunda `data['lc0'] = 100000.0` olarak atanıyor (satır 381) ama `build_model` içinde hiç referans edilmiyor.
- `node_labels` — sadece `print_cv_solution`'da `data.get('node_labels', {})` üzerinden kullanılıyor, `build_model`'e geçirilen parametre olarak hiç kullanılmıyor.

## Neden önemli

`Fc` ve `alpha`'nın varlığı, geliştiricinin CV modeline bir istasyon/yakıt-maliyeti yapısı eklemeyi planladığını ama bunu hiçbir kısıtla tamamlamadığını gösteriyor — bu, [[sorun_sarj_yakit_istasyonlari_kodda_yok]]'ta tarif edilen eksikliğin **somut kod kanıtı**: iskelet var, kısıtlar yok.

## Uygulama (Faz 2, 2026-08-11) — bu sayfa doğrudan hedeflenmedi, ilgili bir düzeltme yapıldı

Bu sayfadaki `Fc`/`alpha`/`g_c`/`k`/`lc0` ölü kod tespiti **Faz 2'de değişmedi** — bu parametreler `src/CV_model_gurobi_fixed.py`'de de hâlâ kullanılmıyor (istasyon yapısı CV'ye eklenmedi, bkz. [[sorun_sarj_yakit_istasyonlari_kodda_yok]]). Ancak **ilgili ama ayrı bir CV tutarsızlığı** (A7) düzeltildi: `h_c` (mesafe başına tüketim oranı) önceden sabit `1.0`'dı, `EnergyConsumptionRate` XML'den hiç okunmuyordu — bu, istasyon eksikliğinden bağımsız ama aynı "CV'nin yakıt/enerji tarafı yarım kalmış" temasının bir başka örneğiydi. `src/xml_data_loader_fixed.py:249-269,289` ile düzeltildi, ayrıca araç-bazlı `h_c_v` sözlüğü eklendi. Detay: [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]].

## Güncelleme (2026-08-22) — 3 parametre artık kullanılıyor (kısmen), alpha tamamen kalktı

`raw/CV_model_gurobi_exact.py`'nin 2026-08-22 yeniden yazımı, bu sayfanın "hepsi ölü kod" iddiasını **kısmen** geçersiz kılıyor:

- **`Fc`**: artık `real_stations = [s for s in Fc if s != 0]` (satır 85) ile filtrelenip CV6/CV7/CV11/CV17 döngülerinde kullanılıyor — ama `xml_data_loader.py` hâlâ `Fc=[0]` döndürdüğü için `real_stations` boş kalıyor, döngüler fiilen boş çalışıyor. Yani **referans ediliyor ama işlevsiz** (öncekinden farkı: en azından artık koda dokunuyor).
- **`g_c`**: artık CV19'da (`+ g_c*(YC[i]-yc[i])` benzeri terim) kullanılıyor; `xml_data_loader.py` `g_c=1.0` sabit döndürüyor.
- **`lc0`**: artık CV19'da `(lc0 + g_c*G[kk[0]])` biçiminde kullanılıyor; `__main__`'de `data['lc0']=40000.0` olarak ayarlanıyor.
- **`alpha`**: **tamamen kaldırıldı** — artık `build_model()` içinde tanımlı bile değil (önceki sürümde tanımlı ama kullanılmıyordu).
- **`k`** (fonksiyon parametresi, talep/demand amaçlı) ve **`node_labels`** (build_model parametresi olarak): hâlâ kullanılmıyor.

Sonuç: 5 "ölü" parametreden 3'ü (`Fc`, `g_c`, `lc0`) artık koda referans ediliyor (ama pratik etkisi hâlâ sıfır, çünkü veri katmanı gerçek istasyon/oran sağlamıyor), `alpha` tamamen silinmiş, `k`/`node_labels` hâlâ ölü. Detay: [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]].

## Sources

- `raw/CV_model_gurobi_exact.py:13-27` (eski, 2026-08-09 hâli)
- `raw/CV_model_gurobi_exact.py:23-29,80-85,335-338` (yeni, 2026-08-22 — Fc/g_c/lc0 artık referans ediliyor)
- `src/xml_data_loader_fixed.py:249-269,289` (ilgili A7 düzeltmesi — Fc/alpha/g_c/k/lc0'ın kendisi hâlâ kullanılmıyor)

## Related

- [[karar_rc13_tam_paket_uygulamasi]] (Ö8, CV'nin `Delta_c`'sine BİLEREK dokunmadı — bu sayfadaki gerekçeyle aynı: CV'de gerçek istasyon hiç yok)
- [[sorun_sarj_yakit_istasyonlari_kodda_yok]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
