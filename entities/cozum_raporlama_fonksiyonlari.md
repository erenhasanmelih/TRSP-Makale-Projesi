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

## Sources

- `raw/CV_model_gurobi_exact.py:210-310`
- `raw/EV_v.1.1.py:394-513`

## Related

- [[format_time_fonksiyonu]]
- [[degisken_yakit_enerji_izleme]]
- [[build_model_fonksiyonu]]
