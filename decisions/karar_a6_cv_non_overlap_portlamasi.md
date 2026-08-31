---
title: Karar (Faz 2, A6) — EV Teknisyen Çakışma Önlemenin CV'ye Portlanması
tags: [karar, faz2, cv, teknisyen-çakışması, a6, non-overlap]
source: src/CV_model_gurobi_fixed.py
date: 2026-08-11
status: güncel
---

# Karar (Faz 2, A6) — EV Teknisyen Çakışma Önlemenin CV'ye Portlanması

## Sorun

karar_ev_teknisyen_cakisma_onleme_mekanizmasi (silindi)'nda belgelenen mantık boşluğu: EV modelinde (`raw/EV_v.1.1.py:225-299`) aynı teknisyenin farklı ikili ekiplerde (bkz. [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]) aynı gün çakışan saatlerde aktif olmasını engelleyen bir mekanizma (`route_start`/`route_end`/`ord_*`/`noov_1`/`noov_2`) var, ama bu mekanizma **CV modelinde hiç yoktu**. CV kodu aynı `itertools.combinations` ekip oluşturma mantığını kullandığı için aynı fiziksel imkânsızlık (bir teknisyenin aynı anda iki farklı CV ekibinde olması) CV modelinde matematiksel olarak engellenmiyordu.

## Karar

EV'deki bloğun tamamı `src/CV_model_gurobi_fixed.py:292-369`'a portlandı: `route_start`/`route_end` sürekli değişkenleri, `y_route` (ekip rota göstergesi) ikilisi, `ord_{tech}_{c1}_{c2}` sıralama değişkeni ve `noov_1`/`noov_2` Big-M kısıtları aynı yapıda eklendi.

Bunu mümkün kılmak için:
- `build_model()` imzasına `crew_members=None, h_c_v=None` parametreleri eklendi (`src/CV_model_gurobi_fixed.py:16-19`), `crew_members = crew_members or {}` ile varsayılan boş sözlük (`:28`).
- `__main__` bloğunda EV'dekine paralel bir `crew_members` sözlüğü kuruldu — bireysel teknisyenler (`crew_members[tech] = [tech]`) ve ikili ekipler (`crew_members[crew_name] = [t1, t2]`) için (`src/CV_model_gurobi_fixed.py:657-673`).

## Doğrulama

R5 problem setinde:
- `noov_*` kısıtı: **48 adet**.
- `ord_*` değişkeni: **24 adet**.
- `route_start_*`/`route_end_*`: **130 adet**.
- Gurobi 13 ile OPTIMAL çözüm, `obj=10116.10` (EV ile aynı).

## Güncelleme (2026-08-22)

Bu kararın portladığı orijinal mekanizma (`raw/EV_v.1.1.py:225-299`, `route_start`/`route_end`/`ord_*`) artık **`raw/EV_v.1.1.py`'de yok** — 2026-08-22 yeniden yazımı bu mekanizmayı tamamen kaldırdı (bkz. karar_ev_teknisyen_cakisma_onleme_mekanizmasi, sayfası 2026-08-22'de silindi). `src/CV_model_gurobi_fixed.py`'deki A6 portlaması **etkilenmedi** (src/ dosyaları değişmedi) — hâlâ geçerli ve çalışır durumda. Ama `raw/`'un kendisi artık aynı kaygıyı (teknisyen çakışması) **farklı, daha genel bir mekanizmayla** (`z`/CV-28, atama-tekilliği tabanlı, zaman penceresi hesabı gerektirmeyen) çözüyor — bkz. [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]. Yani A6'nın çözmeye çalıştığı sorun `raw/`'da da (bağımsız bir yoldan) kapatılmış durumda, src/'deki A6 kaydı hâlâ tarihsel/geçerli.

## Sources

- `src/CV_model_gurobi_fixed.py:16-19,28,292-369,657-673`
- `raw/EV_v.1.1.py:225-299` (portlanan orijinal mekanizma)
- `raw/CV_model_gurobi_exact.py` (mekanizmanın önceden bulunmadığı orijinal dosya)

## Related

- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
