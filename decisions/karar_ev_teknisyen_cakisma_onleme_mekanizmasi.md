---
title: Karar (Kod, EV) — Teknisyen Çakışma Önleme Mekanizması
tags: [karar, kod, ev, teknisyen-çakışması, yeni-bulgu]
source: raw/EV_v.1.1.py
date: 2026-08-09
status: güncel
---

# Karar (Kod, EV) — Teknisyen Çakışma Önleme Mekanizması

## Karar

`EV_v.1.1.py:225-299`'da, `crew_members` verisi mevcutsa aktifleşen bir kısıt bloğu: her ekibin (`crew`) rota başlangıç/bitiş zamanını (`route_start`, `route_end`) izleyip, aynı teknisyeni içeren iki farklı ekip kombinasyonunun (`ord_{tech}_{c1}_{c2}` ikili değişkeni ve Big-M kısıtlarıyla) aynı gün çakışan saatlerde aktif olmasını engelliyor.

## Gerekçe (çıkarım)

[[karar_dinamik_teknisyen_ekibi_itertools_combinations]] ile bir teknisyen birden fazla ikili ekip kombinasyonunda yer alabildiği için (ör. TECH_001, hem `TECH_001__TECH_002` hem `TECH_001__TECH_003` ekiplerinde yer alabilir), fiziksel olarak imkânsız bir durum ortaya çıkabilir: aynı teknisyenin aynı anda iki farklı ekipte rotada olması. Bu mekanizma bu imkânsızlığı matematiksel olarak engelliyor.

## Önemli gözlem

Bu mekanizma **hiçbir yönerge belgesinde anılmıyor** ve **CV modelinde yok** — CV kodu da aynı `itertools.combinations` ekip oluşturma mantığını kullanıyor (bkz. [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]) ama bu çakışma koruması olmadan. Bu, CV modelinde potansiyel bir mantıksal boşluk/hata kaynağı olabilir — aynı teknisyenin iki farklı CV ekibinde aynı gün, çakışan saatlerde göründüğü çözümler CV modelinde matematiksel olarak engellenmiyor.

## Uygulama (Faz 2, 2026-08-11) — CV'ye portlandı

**"Önemli gözlem"deki mantık boşluğu artık kapandı.** `raw/` DEĞİŞTİRİLMEDEN, EV'deki bu mekanizma (`route_start`/`route_end`/`y_route`/`ord_*`/`noov_1`/`noov_2`) `src/CV_model_gurobi_fixed.py:292-369`'a portlandı. Bunun için `build_model()` imzasına `crew_members=None, h_c_v=None` parametreleri eklendi (`src/CV_model_gurobi_fixed.py:16-19,28`) ve `__main__` bloğunda `crew_members` sözlüğü kuruldu (`src/CV_model_gurobi_fixed.py:657-673`).

Doğrulama sayıları (R5 problem seti): `noov_*` kısıtı 48 adet, `ord_*` değişkeni 24 adet, `route_start_*`/`route_end_*` 130 adet. Gurobi 13 ile OPTIMAL çözüm alındı (obj=10116.10).

Detaylı uygulama kaydı: [[karar_a6_cv_non_overlap_portlamasi]].

## Sources

- `raw/EV_v.1.1.py:225-299`
- `src/CV_model_gurobi_fixed.py:16-19,28,292-369,657-673`

## Related

- [[degisken_route_start_route_end_ev]]
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]]
- [[sources/2026-08-09-ev_v1_1]]
- [[sources/2026-08-09-cv_model_gurobi_exact]]
- [[karar_a6_cv_non_overlap_portlamasi]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
