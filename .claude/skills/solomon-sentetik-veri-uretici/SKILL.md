---
name: solomon-sentetik-veri-uretici
description: TRSP için Solomon-tipi (C/R/RC serisi) sentetik problem setleri üretir — müşteri koordinatları, zaman pencereleri, talep büyüklükleri ve EV/CV filo parametreleri xml_data_loader.py'nin okuyabileceği XML formatında. Yeni bir test/deney problem seti gerektiğinde veya mevcut C/R/RC serisi genişletilirken (örn. C15, R15) kullan.
---

# Solomon Sentetik Veri Üretici

`raw/sonuclar/` altındaki mevcut sonuçların (C5, C7, C10, C13, R5, R7, R10, R13, RC5, RC7, RC10, RC13) dayandığı Solomon-tipi problem setleme desenini yeni ölçek/senaryolara genişletmek için kullanılan üretim rehberi. [[trsp-tahmin-veri-muhendisi]] ajanı tarafından kullanılır.

## Ne Zaman Kullanılır

- `decisions/karar_sentetik_veri_uretici_solomon_plani.md`'de planlanan sentetik veri üretici modülün ilk taslağı yazılırken.
- Mevcut C/R/RC serisinin ötesinde yeni bir ölçek (örn. 150-müşteri) veya yeni bir coğrafi dağılım senaryosu (kümelenmiş+rastgele karışık) test edilmek istendiğinde.
- `trsp-karsilastirma-analisti`nin ölçeklenebilirlik analizi için ek veri noktasına ihtiyacı olduğunda.

## Girdi Formatı

```
Seri tipi: C (kümelenmiş) | R (rastgele) | RC (karışık)
Müşteri sayısı: örn. 15
Filo kompozisyonu: CV/EV oranı (örn. %50/%50)
Zaman penceresi sıkılığı: dar | orta | geniş
Coğrafi alan: [0, X] x [0, Y] koordinat kutusu
```

## Çıktı Formatı

- `xml_data_loader.py`'nin beklediği XML şeması (düğüm koordinatları, talep, zaman penceresi, servis süresi + filo/istasyon/çalışan blokları — bkz. `raw/*.xml`, `raw/problem_sets/`, `raw/trsp_problem_sets/` örnekleri).
- Üretim script'i için Python taslağı (numpy ile koordinat/zaman penceresi örneklemesi).
- Üretilen setin özet istatistik tablosu (ortalama zaman penceresi genişliği, talep dağılımı, coğrafi yoğunluk).

## Adımlar

1. `raw/xml_data_loader.py`'yi oku, beklenen XML alan adlarını/yapısını çıkar (kaynak referanslı).
2. Solomon literatüründeki C/R/RC üretim kurallarını (kümelenmiş = k-merkez etrafında Gauss dağılımı; rastgele = uniform; karışık = ikisinin birleşimi) uygula.
3. EV/CV karma filo parametrelerini (batarya kapasitesi, yakıt kapasitesi, istasyon konumları) mevcut `raw/CV_model_gurobi_exact.py`/`raw/EV_v.1.1.py` parametre isimleriyle tutarlı adlandır.
4. Üretilen XML'i **`raw/` klasörüne yazma** — bu klasör salt-okunurdur; üretim script'i taslağını ve örnek çıktıyı wiki sayfasında (`decisions/` veya ayrı bir `sources/` notu) göster, gerçek dosya üretimini kullanıcı `raw/`'a manuel ekler.
5. `decisions/karar_sentetik_veri_uretici_solomon_plani.md`'yi ilerleme durumuyla güncelle.

## Örnek

**Girdi:** "RC15 serisi (karışık kümelenmiş+rastgele, 15 müşteri, %60 EV filo) üret."

**Çıktı:** 15 düğümlük koordinat/zaman penceresi tablosu + XML taslağı + üretim script'i (`numpy.random` tohumlu, tekrarlanabilir) + `karar_sentetik_veri_uretici_solomon_plani.md`'ye eklenen ilerleme notu.

## İlgili

- `decisions/karar_sentetik_veri_uretici_solomon_plani.md`
- `raw/xml_data_loader.py`, `raw/dataset_converter.py`
- İlişkili skill: `topsis-kriter-tasarimci`

**Not:** `raw/` klasörüne asla doğrudan yazma — üretilen veri taslağı önce kullanıcıya sunulur.
