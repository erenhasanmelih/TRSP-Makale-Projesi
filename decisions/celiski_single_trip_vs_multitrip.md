---
title: ÇELİŞKİ — Single-Trip (Model) vs Multi-Trip (Kod)
tags: [çelişki, kısıt, araç-kullanımı, kritik]
source: raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx
date: 2026-08-09
status: güncel
---

# ÇELİŞKİ — Single-Trip (Model) vs Multi-Trip (Kod)

## ÇELİŞKİ

**Matematiksel model tarafı:** Kısıt (3), her aracın (v) depodan (0) gün içinde **en fazla bir kez** çıkış yapabilmesini güvence altına alır (single-trip sınırı).

**Kod tarafı:** `CV_model_gurobi_exact.py` içinde `c4_multitrip_{v}` isimli bir kısıt eklenmiş; bir aracın depodan çıkış sayısını sınırlayarak **günde üç defaya kadar** tur atmasına izin veriyor (multi-trip).

Bu iki kural doğrudan çelişiyor: aynı araç kullanım kısıtı, model belgesinde "en fazla 1", kodda "en fazla 3" olarak tanımlanmış. Henüz hangisinin doğru/nihai kural olacağı netleşmemiş — silinmiyor, burada işaretli tutuluyor.

## Neden önemli

Bu, sadece bir kod hatası değil, olası bilinçli bir operasyonel esneklik kararı olabilir (bir aracın günde birden fazla tur atması gerçek hayatta makul bir senaryo). Makale yazımı öncesi hangi kuralın doğru kabul edileceğine karar verilmeli.

## ÇELİŞKİ (güncelleme — Stage 2 kod doğrulaması, 2026-08-09)

Stage 2 ingest'inde `raw/CV_model_gurobi_exact.py` ve `raw/EV_v.1.1.py` satır satır okundu. **Docx'ün iddia ettiği `c4_multitrip_{v}` kısıtı mevcut kodun hiçbir yerinde bulunamadı.**

- CV kodunda (`CV_model_gurobi_exact.py:53-54`): `m.addConstr(gp.quicksum(x[0,j,v,t] ...) <= 1, name=f"c4_{v}")` — **tek sefer**, matematiksel modelin Kısıt (3)'üyle uyumlu.
- EV kodunda (`EV_v.1.1.py:134-139`): `MAX_ROUTES_PER_VEHICLE = 1` sabitiyle sınırlı, aynı şekilde **tek sefer**.

Yani gerçek çelişki artık "model vs kod" değil, **"yönerge belgesinin kod tarifi" vs "kodun mevcut hâli"** arasında. İki olası açıklama: (a) docx, kodun daha önceki bir sürümünü tarif ediyor ve multi-trip özelliği sonradan kaldırılmış; (b) docx yazılırken bir yanlış hatırlama/karışıklık olmuş. Dosya tarihleri bunu çözmüyor: docx'ler 7 Ağustos 2026, python dosyaları 18-29 Mayıs 2025 tarihli — yani docx, python dosyalarından çok sonra yazılmış olmasına rağmen kodda olmayan bir kısıttan bahsediyor. **Bu maddeyi silmiyoruz, iki kaynak arasındaki tutarsızlık olarak burada işaretli tutuyoruz.**

## Not (Faz 2, 2026-08-11) — çelişki hâlâ çözülmedi, bağımsız üçüncü doğrulama eklendi

Faz 1/2 analiz çalışması (7 sorun A1-A7/C1-C2 tespiti sırasında) kodu bağımsız olarak yeniden inceledi ve aynı sonuca ulaştı: hem `raw/CV_model_gurobi_exact.py` hem `raw/EV_v.1.1.py` **tek-sefer** kısıtlı, docx'ün iddia ettiği "3 tura kadar" (`c4_multitrip_{v}`) hiçbir yerde bulunamadı. Faz 2'nin `src/` kopyaları da bu davranışı **değiştirmedi** — `MAX_ROUTES_PER_VEHICLE = 1` aynen korundu (`src/EV_v_1_1_fixed.py:20`), CV tarafında da tek çıkış kısıtı (`c4_{v}`) dokunulmadan taşındı. Yani bu madde Faz 2'nin kapsamına (A1-A7, C1-C2) girmedi; docx↔kod çelişkisi **çözülmeden kalıyor**, sadece kodun tek-sefer davranışının üçüncü kez (Stage 2 + Faz 2 analizi) doğrulanmış olması bu maddenin "docx hatası/eski sürüm" açıklamasını biraz daha güçlendiriyor. Kesin çözüm için hâlâ kullanıcı kararı gerekiyor.

## Sources

- `raw/Yönergelerimiz/kodda ve matematiksel modeldeki farklılıklar.docx`
- `raw/CV_model_gurobi_exact.py:53-54`
- `raw/EV_v.1.1.py:16-18,134-139`
- `src/EV_v_1_1_fixed.py:20` (MAX_ROUTES_PER_VEHICLE=1, değişmedi)

## Related

- [[sources/2026-08-09-kodda_ve_matematiksel_modeldeki_farkliliklar]]
- [[sources/2026-08-09-cv_model_gurobi_exact]]
- [[sources/2026-08-09-ev_v1_1]]
- [[model_karar_degiskenleri_ve_parametreleri]]
- [[karar_src_klasoru_ve_raw_izolasyonu]]
