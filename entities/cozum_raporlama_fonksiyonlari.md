---
title: Çözüm Raporlama Fonksiyonları (print_cv_solution, print_ev_solution)
tags: [entity, fonksiyon, raporlama, çıktı]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Çözüm Raporlama Fonksiyonları

## print_cv_solution(data, model) — `CV_model_gurobi_exact.py:210-310`

Gurobi çözümü bulunduktan sonra, her araç/ekip/gün için rotayı Türkçe emoji'li konsol çıktısı olarak basar: depodan çıkış saati, her müşteriye varış/hizmet/ayrılış saati, öğle molası varsa saatleri, depoya dönüş saati ve toplam rota süresi.

## print_ev_solution(data, model) — `EV_v.1.1.py:394-513`

Aynı amaçla ama EV'ye özgü ek bilgilerle: her adımda **Varış SoC**, **Çıkış SoC**, **Şarj** miktarı sütunları var; istasyon düğümlerinde (`S_set`) şarj miktarı ve süresi ayrıca satırlanıyor. `charge_amount()` iç yardımcı fonksiyonu, bir düğümdeki `YE - ye` farkını (şarj edilen miktar) hesaplıyor.

## Ortak özellik

Her ikisi de rotaları `x[i,j,v,t].X > 0.5` filtreleyerek arc listesine, sonra `next_map` ile sıralı bir rotaya (`route`) dönüştürüyor — aynı algoritma iki dosyada da tekrarlanıyor (kod paylaşımı/kopyalama izlenimi, bkz. [[build_model_fonksiyonu]]).

## Güncelleme (2026-08-22) — EV artık CV ile simetrik, ikisi de çoklu-sefer farkında

`raw/CV_model_gurobi_exact.py:430-583` ve `raw/EV_v.1.1.py:379-520`'deki 2026-08-22 sürümleri, önceki sürümdeki asimetriyi (EV'nin SoC/şarj sütunlu özel tablo formatı, Tee/docx otomatik kaydı) ortadan kaldırdı — **iki fonksiyon artık neredeyse birebir aynı** (yalnızca emoji ve başlık farklı: CV `📌`, EV `🔋`). İkisi de artık **çoklu sefer farkında** (CV-4/EV-4, ≤3): `depot_departures`/`next_map` ile arc'lar önce sefer (trip) listelerine ayrıştırılıyor, her sefer ayrı raporlanıyor. Çıktı hâlâ `.txt` dosyasına yazılıyor (`Operasyon_Raporu_<problem>.txt` / `Operasyon_Raporu_EV_<problem>.txt`), EV artık `.docx` üretmiyor (bkz. karar_ev_otomatik_docx_raporlama, sayfası 2026-08-22'de silindi). Aynı arc→trip ayrıştırma mantığı üçüncü kez `raw/solution_validator.py`'de de tekrarlanıyor — bkz. [[solution_validator_fonksiyonlari]].

## Sources

- `raw/CV_model_gurobi_exact.py:210-310` (eski, 2026-08-09 hâli)
- `raw/EV_v.1.1.py:394-513` (eski, 2026-08-09 hâli)
- `raw/CV_model_gurobi_exact.py:430-583` (yeni, 2026-08-22)
- `raw/EV_v.1.1.py:379-520` (yeni, 2026-08-22)

## Related

- [[format_time_fonksiyonu]]
- [[degisken_yakit_enerji_izleme]]
- [[build_model_fonksiyonu]]
- [[sorun_rapor_mola_suresi_3600_vs_ll_el]]
- [[sorun_rapor_unicode_cokme_log_print]]
- [[sorun_coklu_sefer_zaman_sirasi_ihlali]]
