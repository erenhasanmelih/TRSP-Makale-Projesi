---
title: Makale Adımlar ve Düzenlemeler
tags: [yönerge, makale-yapısı, literatür-atıf, hibrit-algoritma, model-eksikleri]
source: raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx
date: 2026-08-09
status: güncel
---

# Makale Adımlar ve Düzenlemeler

## Amaç

Makalenin ana amacını netleştirmek, mevcut Gurobi kodundaki teorik/yapısal eksiklikleri (CV ve EV ayrı ayrı) tespit etmek, literatür atıf haritasını çıkarmak ve hibrit algoritmanın geliştirme sırasını (solution methodology) tanımlamak.

## Ne yapıldı

**1. Makalenin ana amacı:** Telekom saha operasyonlarını (TRSP) optimize eden, CV ve EV filolarını operasyonel/ekonomik/çevresel (karbon) açıdan kıyaslayan çok amaçlı bir Karar Destek Sistemi (DSS) mimarisi sunmak. Problemin NP-Zor doğası kanıtlanacak, kesin yöntemlerin (Gurobi) yetersizliği gösterilecek; çözüm CatBoost + TOPSIS + Branch-and-Bound + VND'yi harmanlayan bir hibrit algoritma olacak.

**2. Matematiksel modeldeki hatalar/eksikler:**

*CV için:*
- Yetkinlik Matrisinin Yokluğu — kodda `Ti[j]` ile Python seviyesinde filtreleme yapılmış; makalede deterministik bir parametre (renk/yetkinlik matrisi) olarak Gurobi kısıtlarına açıkça yedirilmeli.
- Gevşek Big-M ve Alt-Tur (Sub-tour) Zafiyeti — MTZ (Miller-Tucker-Zemlin) alt-tur önleme ve çok büyük Big-M kullanımı, Branch-and-Bound'un budama yapmasını engelliyor; Big-M, teknisyenin o günkü maksimum mesai bitiş süresiyle sınırlandırılmalı.

*EV için (kod EV için "çalışamaz durumda" olarak nitelendiriliyor):*
- Yakıt Kurgusunun Yanlışlığı — kodda `yc`/`YC` ile izlenen enerji tüketimi sadece mesafeye bağlı; gerçekte taşınan yüke ve hıza bağlı doğrusal olmayan bir yapı olmalı.
- Kısmi Şarj (Partial Recharging) Dinamiği Yok — EV'ler bataryayı tam doldurmak zorunda değil, kodda bu esneklik yok.
- Klon Düğüm (Node Replication) Eksikliği — EV'ler rotanın ortasında bir istasyona birden fazla kez uğrayabilmeli; model şarj istasyonları için klonlanmış (dummy) düğümler ve giriş-çıkış akışları üretmeli.

**3. Literatür haritalaması (hangi makale nereye atıf):**
- Acar & Altın (2025) → problem tanımı + çok depolu/renkli yapı (MD-GCTSP-TW temeli).
- Acar et al. (2025) → çok amaçlı optimizasyon + iş yükü dengeleme, ε-Constraint yöntemi.
- Ghasemi Saghand et al. (2019) → kesin yöntemlerin sınırları, Branch-and-Bound zorluğu.
- Konur & Golias (2013) → zaman belirsizlikleri, meta-sezgisel ihtiyacı, maliyet istikrarı.

**4. Melez algoritma mimarisi ve geliştirme sırası:**
- Adım 1: Veri Ön İşleme ve Kümeleme — CatBoost + TOPSIS modülleri ile aciliyet/yetkinliğe göre düğümler alt kümelere ayrılır.
- Adım 2: Başlangıç Çözümü Üretimi (Warm-Start via Sweep Algorithm).
- Adım 3: Yerel Kesin Çözümler — küçük kümeler (5-7 müşteri) Gurobi'ye (Branch-and-Bound) gönderilir.
- Adım 4: Gelişmiş Meta-Sezgisel Arama (VND) — Swap, Insert, Reverse, Drop/Add operatörleri; k-drop/add sarsma (shaking) mekanizmasıyla yerel optimuma takılmayı önler.

## Anahtar noktalar

- Bu belge "kodda ve matematiksel modeldeki farklılıklar.docx" ile büyük ölçüde örtüşüyor ama ek olarak EV kodunun "çalışamaz durumda" olduğunu daha sert biçimde vurguluyor ve MTZ alt-tur önleme kısıtlarına özel olarak değiniyor (diğer belgede MTZ adı geçmiyor, sadece Big-M genel olarak geçiyor).
- Hibrit algoritma mimarisi burada 4 net adıma indirgenmiş: Kümeleme → Warm-start → Yerel B&B → VND. Bu, Full Path.docx'teki Adım 3 ile aynı ama biraz daha detaylı.
- CatBoost/TOPSIS kullanımı burada "veri ön işleme katmanı" olarak, dinamik tahminleme belgesinde ise "haftalık talep tahmini + iptal olasılığı" olarak iki farklı bağlamda geçiyor — aynı araçların farklı kullanım noktaları, çelişki değil tamamlayıcı.

## Kararlar

- [[karar_hibrit_algoritma_mimari_sirasi]]
- [[karar_literatur_temelli_problem_tanimi_md_gctsp_tw]]
- [[sorun_ev_enerji_tuketim_modeli_basitlestirilmis]]
- [[karar_klon_dugum_sarj_istasyonu_plani]]

## Açık konular

- MTZ alt-tur önleme kısıtlarının kodda `tau` değişkeni üzerinden zaten (zaman ilerlemesi kısıtı olarak, `c8_zaman_ilerleme`) dolaylı biçimde var olup olmadığı Stage 2'de doğrulanmalı.
- "EV kodu çalışamaz durumda" iddiası, `EV_v.1.1.py` dosyasının fiilen çalıştırılabilir bir model kurup kurmadığı Stage 2'de teyit edilmeli — bu ifade dosyanın v1.1 olduğu göz önüne alınca, iddianın hangi versiyon için geçerli olduğu belirsiz. [[ÇELİŞKİ]] adayı.

## Sources

- `raw/Yönergelerimiz/makale adımlar ve düzenlemeler.docx` (tam metin)

## Related

- [[catboost]]
- [[topsis]]
- [[vnd]]
- [[partial_recharging]]
- [[klon_dugum_node_replication]]
- [[model_karar_degiskenleri_ve_parametreleri]]
