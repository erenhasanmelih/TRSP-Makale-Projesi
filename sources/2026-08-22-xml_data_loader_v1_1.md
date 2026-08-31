---
title: xml_data_loader.py (v1.1) — Ortak Veri Hazırlama Katmanı (İlk Source Sayfası)
tags: [kaynak, kod, veri-yukleme, cv, ev, v1.1]
source: raw/xml_data_loader.py
date: 2026-08-22
status: güncel
---

# xml_data_loader.py (v1.1) — Ortak Veri Hazırlama Katmanı

## Amaç

`raw/xml_data_loader.py`, hem `CV_model_gurobi_exact.py` hem `EV_v.1.1.py`'nin kullandığı ortak veri hazırlama katmanıdır. Bu dosya için **daha önce hiç ayrı bir `sources/` sayfası açılmamıştı** (sadece `entities/` sayfalarından dolaylı referans verilmişti) — bu, ilk özel source sayfasıdır. 2026-08-22'de içeriği değişti (45 satır fark, 355→362 satır).

## Fonksiyon envanteri

- **`_strip_hash_comments(line)` / `_safe_parse_xml(path)`** (satır 8-32): XML dosyalarını okumadan önce `#` ile başlayan satır-içi yorumları (tırnak içindekiler hariç) temizliyor — standart `ET.parse()`'ın desteklemediği bir esneklik.
- **`haversine(lat1,lon1,lat2,lon2)`** (satır 35-42): iki koordinat arası büyük-daire mesafesini metre cinsinden hesaplıyor; `d`/`tt` matrislerinin kaynağı.
- **`load_problem_instances(root_dir, subdirs)`** (satır 61-119): `trsp_problem_sets/` altındaki XML problem dosyalarını tarayıp depo+teslimat düğümlerini ayrıştırıyor.
- **`parse_vehicle_file(vehicle_xml_path, expected_type=None)`** (satır 122-157): araç XML'lerini okuyor. `vehicle_attrs` sözlüğü şu alanları içeriyor: `Type`, `MaxSpeed`, `Range`, `BatteryCapacity`, `SoC`, `MaximumLoadCapacityKg`. **`EnergyConsumptionRate` alanı okunmuyor** — bkz. [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]].
- **`parse_charging_stations(station_xml_path)`** (satır 160-173): şarj istasyonu XML'ini okuyor (EV için).
- **`prepare_cv_data_from_instance(...)`** (satır 213-269): CV modeline geçirilecek `data` dict'ini üretiyor. `'h_c': 1.0, 'g_c': 1.0` sabit (satır 264-265) — bkz. yukarıdaki regresyon notu. `'Fc': [0]` sabit (satır 252) — gerçek istasyon listesi hâlâ yok (bkz. [[sorun_sarj_yakit_istasyonlari_kodda_yok]]). `es_val=0.0, ls_val=32400.0, el_val=14400.0, ll_val=21600.0` varsayılan mesai/mola parametreleri (satır 218-221) — bkz. [[sorun_hardcoded_mola_parametreleri]] güncellemesi (mola penceresi artık `el`/`ll` farkı üzerinden, 14400-21600 = 2 saatlik bir pencere; eski `break_min/break_max` 20 dakikalık pencereden farklı).
- **`prepare_ev_data_from_instance(...)`** (satır 272-362): EV modeline geçirilecek `data` dict'ini üretiyor. `Q` (batarya kapasitesi) doğru alandan (`BatteryCapacity`) okunuyor — yorum satırı (308-311) bunun eski bir hatanın (`MaximumLoadCapacityKg=-1.0` okunması) düzeltmesi olduğunu açıkça belirtiyor. `h_e = BatteryCapacity/Range`, `g_e = 3600/charging_power_w` (22 kW varsayımı, satır 314-328) — Fiat E-Doblo teknik verilerinden türetilmiş, dinamik (CV'nin aksine).

## Önemli gözlem — CV ve EV veri hazırlama arasındaki asimetri

EV tarafı (`prepare_ev_data_from_instance`) tüketim oranını (`h_e`) araç teknik verisinden (`BatteryCapacity/Range`) **dinamik olarak türetiyor**; CV tarafı (`prepare_cv_data_from_instance`) aynı işi yapmıyor, `h_c`'yi sabit `1.0` bırakıyor — oysa `parse_vehicle_file` her iki araç tipi için de aynı fonksiyon, XML'de muhtemelen bir `EnergyConsumptionRate` alanı mevcut (Faz 2'nin A7 düzeltmesi bunu okuyordu). Bu asimetri, CV ve EV veri hazırlama kodunun bağımsız/farklı özenle yazıldığı izlenimini güçlendiriyor.

## Sources

- `raw/xml_data_loader.py` (tam dosya, 362 satır, 2026-08-22)
- `yeni dosyalarım/Codes_rev_v1.1/Ana_Kodlar_ve_Açıklamaları.docx`

## Related

- [[sources/2026-08-22-cv_model_gurobi_exact_v1_1]]
- [[sources/2026-08-22-ev_v1_1_rewrite]]
- [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]]
- [[sorun_sarj_yakit_istasyonlari_kodda_yok]]
- [[sorun_hardcoded_mola_parametreleri]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
