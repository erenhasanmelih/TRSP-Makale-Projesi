---
title: Karar (UYGULANDI) — RC13 Asgari Hızlandırma Paketi (Ö1+Ö2+Ö6) raw/'a İşlendi
tags: [karar, uygulandi, rc13, yetkinlik-filtresi, arac-agregasyonu, istasyon-dusurme, mip-formulasyon, cv, ev, gurobi]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py; raw/xml_data_loader.py; raw/solution_validator.py
date: 2026-08-28
status: güncel
---

# Karar (UYGULANDI) — RC13 Asgari Hızlandırma Paketi

> **GÜNCELLEME (2026-08-31):** Bu sayfadaki RC13/RC15/R10/RC10 objektif
> değerleri de [[karar_5_8_teknisyen_bug_fix]] öncesi (5/8 teknisyen)
> koşumlardır — RC13/RC15 için artık geçersiz, bkz.
> [[karar_rc13_tam_paket_uygulamasi]] güncelleme notu (19938.07 / 21851.58).
> R10/RC10/C5/R5/RC5 bu bug fix'ten muhtemelen etkilenmedi (tüm beceriler
> zaten tek aktif teknisyenle karşılanabiliyordu) ama bu **yeniden
> doğrulanmadı** — ihtiyatlı olun.
>
> **Durum: UYGULANDI (2026-08-28).** [[sorun_rc13_darbogaz_kok_neden_analizi]]'nde
> teşhis edilen darboğaza karşı önerilen 7 iyileştirmeden Eren'in onayladığı
> **Ö1 (yetkinlik filtresi) + Ö2 (araç indisi agregasyonu) + Ö6 (istasyon
> düşürme)**, artı `req_skills_unique` için `list(set(...))` →
> `sorted(set(...))` düzeltmesi, doğrudan `raw/CV_model_gurobi_exact.py`,
> `raw/EV_v.1.1.py`, `raw/xml_data_loader.py` ve `raw/solution_validator.py`
> içine işlendi. Ö3/Ö4/Ö5/Ö7 **uygulanmadı** (aşağıda §3'te neden önemli
> olduğu açıklanıyor).

## 1. ÖNEMLİ DÜZELTME — "asgari paket" iddiası yanlış karakterize edilmişti

[[sorun_rc13_darbogaz_kok_neden_analizi]] §6'nın giriş notu şunu iddia
ediyordu:

> "Asgari paket (ablasyonla doğrulanmış): Ö1 + Ö2 + Ö6 ... RC13'ü **2.7 s'de
> kanıtlanmış optimale** getiriyor (-dfj satırı, §4.3)."

Bu **YANLIŞTIR** ve bu oturumda düzeltilmiştir. §4.3'teki "-dfj" ablasyon
satırı, B9 TAM konfigürasyonundan (crew_fix+aggregate+bwp+arc_fix+min_veh+
tight_m+drop_st, hepsi birlikte) yalnızca DFJ'yi çıkarır — yani 2.7 s rakamı
Ö1+Ö2+Ö3(min_veh)+Ö4(bwp+arc_fix)+Ö6+Ö7(tight_m)'nin **HEPSİNİN BİRLİKTE**
sonucudur, yalnızca üç bileşenin değil. Bu karışıklık, kullanıcıya "Ö1+Ö2+Ö6
saniyeler içinde çözer" biçiminde yanlış bir beklenti olarak aktarılmış ve
onay bu beklentiyle verilmiştir. Aşağıdaki §2, GERÇEKTEN yalnızca Ö1+Ö2+Ö6
uygulandığında ölçülen sonucu raporlar.

## 2. Gerçek ölçüm — yalnızca Ö1+Ö2+Ö6 (bu sayfanın uyguladığı küme)

Test yöntemi: `raw/` modülleri doğrudan import edilip (`build_model`)
`__main__`'daki ekip/yetkinlik kurulum mantığı bire bir tekrarlanarak
koşuldu (script `raw/` DIŞINDA,
`%TEMP%\...\scratchpad\test_helpers.py`). `Seed=1`, `MIPGap=1e-4`,
varsayılan Gurobi parametreleri (raw/'un `__main__`'ındaki
`NoRelHeurTime=600`/`MIPFocus=2`/`Heuristics=0.15` **kullanılmadı** —
sade parametrelerle bile sonuç aşağıdaki gibidir).

| Örnek | Model | Durum | Amaç | Gap | Süre | Düğüm | `solution_validator` |
|---|---|---|---|---|---|---|---|
| C5 | CV | OPTIMAL | 8291.2 | %0.00 | ~0 s | 1 | valid=True |
| C5 | EV | OPTIMAL | 8291.2 | %0.00 | ~0 s | — | valid=True (`stations_dropped=True`) |
| R5 | CV/EV | OPTIMAL | 10116.1 | %0.00 | ~0 s | 1 | valid=True |
| RC5 | CV/EV | OPTIMAL | 7933.0 | %0.00 | ~0 s | 1 | valid=True |
| R10 | CV | OPTIMAL | 14335.3 | %0.00 | 0.6 s | 2681 | valid=True |
| R10 | EV | OPTIMAL | 14335.3 | %0.00 | 0.5 s | 2074 | valid=True |
| RC10 | CV | OPTIMAL | 10588.4 | %0.00 | 0.7 s | 2908 | valid=True |
| RC10 | EV | **OPTIMAL** | **10729.2** | %0.00 | 0.6 s | 3482 | valid=True |
| **RC13** | **EV** | **OPTIMAL** | **20666.99** | **%0.00** | **67.4 s** | 131 745 | valid=True |
| **RC13** | **CV** | **OPTIMAL** | **20666.99** | **%0.00** | **106.4 s** | 187 003 | valid=True |
| RC15 | EV | zaman aşımı (300 s→180 s test) | 23948.4 | %8.05 | 180 s | 216 690 | — |
| RC20 | EV | çözüm yok | — | — | 180 s | 161 161 | — |

**Öne çıkan sonuçlar:**

1. **RC13 (hedef örnek): 900 s'de SIFIR fizibil çözümden → ~1-2 dakikada
   KANITLANMIŞ OPTİMALE.** Hem CV hem EV, `sorun_rc13_darbogaz_kok_neden_analizi`
   §1'de bulunan optimal değeri (20667.0) birebir doğruluyor. Bu, "2.7 s"
   değil ama yine de raw/ eşdeğerinin (900 s, 0 çözüm) yanında **muazzam** bir
   kazanç ve **dürüst** bir rakamdır.
2. **R10/RC10 artık kanıtlanmış optimal (<1 s).** Önceki en iyi kayıt
   ([[karar_r_max_dinamik_turetme]] §9.0) 600 s'de %25-58 gap'liydi;
   şimdi aynı örnekler 1 saniyenin altında kanıtlanmış optimale ulaşıyor.
3. **RC10 EV'de yeni bir en iyi bilinen değer bulundu: 10729.2** (önceki
   kayıtlar 13899.5 / 14727.5 idi, hiçbiri kanıtlanmış optimal değildi).
   Bu bir regresyon değil — model KESİNLEŞTİ, önceki değerler zaten
   kanıtlanmamış ara çözümlerdi.
4. **Sınır: RC15/RC20'de yetersiz.** RC15 180 s'de %8 gap'te kalıyor
   (muhtemelen daha uzun sürede kapanır), RC20 180 s'de hiç fizibil çözüm
   bulamıyor. Bu beklenen bir sonuçtur —
   [[sorun_rc13_darbogaz_kok_neden_analizi]] §9'un "kazanç `n` ile azalır"
   gözlemiyle tutarlı; Ö3/Ö4/Ö5/Ö7 uygulanmadan bu ölçekte paket yetersiz
   kalıyor (bkz. §3).

## 3. Ö3/Ö4/Ö5/Ö7 NEDEN UYGULANMADI

Eren yalnızca Ö1+Ö2+Ö6'yı onayladı; bu sayfa yalnızca onu uyguladı. §1'deki
düzeltmeyle birlikte artık açık: RC13'ün **kanıtlanmış** optimale ulaşması
için asıl "ucuz" ve yüksek kazançlı üç bileşen (Ö1, Ö2, Ö6) tek başına
YETERLİ olmuştur (67-106 s, kabul edilebilir bir süre), ama daha büyük
örnekler (RC15/RC20) veya daha sıkı zaman bütçeleri için Ö3
(`min_veh` geçerli eşitsizliği) ve Ö4 (mola penceresi yayılımı, yalnız EV)
hâlâ ek kazanç sağlayabilir — bunlar `raw/`'a **işlenmemiştir**, ayrı bir
onay gerektirir.

## 4. Uygulama — dokunulan yerler

### Ö1 — Yetkinlik filtresini x/w üzerinde uygula
`raw/CV_model_gurobi_exact.py` ve `raw/EV_v.1.1.py`, `x`/`w` değişkenleri
oluşturulduktan hemen sonra: `(i,j) in At`, `kk in K` için, `i` veya `j`
müşteriyse (`in C`) ve `kk` o düğümün `Ti_K` listesinde değilse
`x[i,j,kk].UB = w[i,j,kk].UB = 0.0`.

**Tasarım notu (teşhis sayfasındaki `crew_fix`'ten sapma):** Teşhis
sayfasındaki ölçüm, x'i DEĞİŞKEN DOMAIN'İNDEN çıkararak (`addVars` çağrısına
verilmeden) yapılmıştı (`NumVars` 28703→8615). Burada bunun yerine `UB=0`
sabitlemesi seçildi: ~15 kısıt bloğunun `x[i,j,kk]`/`w[i,j,kk]` erişimini
(çoğu `for kk in K: ... x[i,j,kk]` biçiminde, domain daraltmayla KeyError
riski taşırdı) bozmadan Gurobi presolve'un bunları birinci adımda (sabit
değişken elemesi) kaldırmasını sağlar. Pratik B&B etkisi domain
daraltmayla AYNIDIR (ölçümler §2'de bunu doğruluyor); yalnızca ham
(presolve öncesi) `NumVars` metriği teşhis sayfasındaki kadar düşük
görünmez.

### Ö2 — Homojen filoda araç indisini kaldır
Her iki `build_model`'de, `K = [(v,t) for v in V for t in T]` tanımından
hemen önce: `aggregate_fleet = len({round(G[v],6) for v in V}) <= 1`
(CV) / aynısı `Q` ile (EV). `True` ise `K = list(T)` (kk artık `(v,t)`
tuple'ı değil, yalnızca `t` — bir crew id string'i).

Bu, kodun ~15 yerinde `_, t_ = kk` / `v_, t_ = kk` unpacking'ine ve 3-4
yerde `Q[kk[0]]`/`G[kk[0]]` (araç-spesifik kapasite) erişimine dayanıyordu;
hepsi iki yardımcı fonksiyonla merkezi hale getirildi:
```python
def _t_of(kk): return kk[1] if isinstance(kk, tuple) else kk
def _Qk(kk):   return _Q_const if aggregate_fleet else Q[kk[0]]  # (CV: _Gk/G)
```
`Ti_K` de aynı şekilde dallandırıldı (aggregate modda `(v,t)` tuple'ı
DEĞİL, düz `t` listesi — aksi hâlde Ö1'in yetkinlik filtresi hiçbir zaman
eşleşmez ve tüm `x`/`w` yanlışlıkla sıfırlanırdı; bu, uygulama sırasında
yakalanan bir hataydı).

**EV-22/EV-23 (CV-27/28) yeniden yazıldı:** "her araç en fazla bir ekibe"
kısıtı, araç boyutu olmadığında anlamsız hâle geliyor; agregatize
karşılığı `Σ_t z_veh[t] <= |V|` (toplam aktif ekip sayısı fiziksel araç
sayısını aşamaz) — CV-27/EV-22'nin orijinal gerekçesiyle (günlük tekil
atama, zaman-örtüşmesi DEĞİL) matematiksel olarak eşdeğerdir. CV-28/EV-23
(ham teknisyen tekilliği) değişmeden kalır, yalnızca toplam ifadesi
`v` boyutunu düşürür.

**Kaybolan bilgi (bilinçli, dengelenmiş bir tercih):** Aggregate modda
model artık HANGİ fiziksel aracın hangi ekibe gittiğini TEMSİL ETMİYOR
(yalnızca "en fazla |V| ekip aktif" garantisi var). `print_cv_solution`/
`print_ev_solution` bu durumda araç adı yerine `"Arac?"` yer tutucusu
yazıyor. `solution_validator.validate_solution`'ın "Kontrol 2" (araç
çakışması) kısmı, aggregate modda ANLAMSIZ hâle geldiği için (fiziksel
araç bilgisi yok) YENİDEN YAZILDI: artık zaman ekseninde aynı anda aktif
ekip sayısının `|V|`'yi aşıp aşmadığını (sweep-line ile) kontrol ediyor —
bu, EV22/CV27'nin agregatize kısıtının SOLVER TARAFINDAN gerçekten
sağlandığının bağımsız bir regresyon testidir.

### Ö6 — Enerji hiç bağlamıyorsa istasyonları düşür
`raw/xml_data_loader.py`, `prepare_ev_data_from_instance` içine: düğüm
kümesi kurulmadan ÖNCE istasyonsuz bir "ön-test" yapılır (depo+müşteri
mesafeleriyle `derive_r_max` çağrılır); test `max_route_distance <=
range_m` derse (`karar_r_max_dinamik_turetme` §3-4'teki birleştirme
baskınlığı argümanının AYNISI) istasyonlar (`S=[]`) hiç eklenmeden CV ile
aynı istasyonsuz yapı kurulur. `data['stations_dropped']` bayrağıyla
izlenebilir; `__main__` çıktısına yazdırılır.

### `sorted(set(...))` düzeltmesi
`raw/CV_model_gurobi_exact.py:969` ve `raw/EV_v.1.1.py:953`:
`req_skills_unique = list(set(delivery_skills))` →
`sorted(set(delivery_skills))`. Python'un süreç bazında rastgeleleşen
string hash'i nedeniyle ekip adlarının/`T` sıralamasının koşumdan koşuma
değişmesini önler — `karar_r_max_dinamik_turetme` §9.1'de "Gurobi'nin
sezgisel şansı" olarak yorumlanan `R_max=3`/`R_max=1` yön tersine
dönmesinin muhtemel gerçek nedeniydi
([[sorun_rc13_darbogaz_kok_neden_analizi]] §7 yan bulgu 1).

## 5. Doğrulama yöntemi

`raw/` dosyaları DOĞRUDAN import edilip test edildi (script `raw/`
dışında: `%TEMP%\...\scratchpad\test_helpers.py`), `raw/`'un kendi
`__main__` bloğu ÇALIŞTIRILMADI (interaktif `input()` içerdiğinden). Her
koşumda `raw/solution_validator.validate_solution()` çağrıldı, hepsi
`valid=True` döndü.

**Heterojen filo fallback'i de test edildi** (mevcut veri setinde
tetiklenmediği için elle simüle edildi: C5'te bir aracın kapasitesi
%50 artırılarak `aggregate_fleet=False` zorlandı, CV ve EV'de ayrı ayrı):
model hatasız kuruldu, aynı optimal değere (8291.2) ulaştı,
`solution_validator`'ın ESKİ (araç-çakışması) kontrol yolu da hatasız
çalıştı. Bu, Ö2'nin İKİ kod yolunun da (aggregate VE aggregate-olmayan)
sağlam olduğunu gösterir.

## 6. Sınırlamalar

- Yalnızca RC13 hedefliydi; RC15/RC20 gibi daha büyük örneklerde paket
  tek başına yetersiz (§2 madde 4). Ö3/Ö4 bu örneklerde muhtemelen gerekli.
- `print_cv_solution`/`print_ev_solution`'ın aggregate moddaki `"Arac?"`
  yer tutucusu, gerçek bir rapor için (makale/tez ekleri) fiziksel araç
  atamasının post-processing ile yapılmasını gerektirir — bu adım
  UYGULANMADI (yalnızca placeholder var).
- Test scripti (`test_helpers.py`) `raw/`'un `__main__`'ındaki
  `NoRelHeurTime=600`/`MIPFocus=2`/`Heuristics=0.15` ayarlarını
  KULLANMADI; gerçek `__main__` koşumunda süre biraz farklı çıkabilir
  (muhtemelen benzer veya daha iyi, çünkü `NoRelHeurTime=600` artık
  gereksiz bir ısınma bütçesi olabilir — [[sorun_rc13_darbogaz_kok_neden_analizi]]
  §1'deki B9 gözlemiyle tutarlı).

## Sources

- `raw/CV_model_gurobi_exact.py` — `aggregate_fleet`/`_t_of`/`_Gk` bloğu,
  Ö1 UB=0 bloğu, CV27/28 dallanması
- `raw/EV_v.1.1.py` — aynısı, simetrik (`_Qk`)
- `raw/xml_data_loader.py` — `prepare_ev_data_from_instance` içindeki
  istasyonsuz ön-test bloğu
- `raw/solution_validator.py` — aggregate mod Kontrol 2 yeniden yazımı
- Test: `%TEMP%\...\scratchpad\test_helpers.py` (raw/ dışında)

## Related

- [[karar_rc13_tam_paket_uygulamasi]] (bu paketin üstüne Ö3+Ö4+Ö7a+Ö7b+Ö8 ekleyen sonraki karar)
- [[sorun_rc13_darbogaz_kok_neden_analizi]] (bu kararın uyguladığı teşhis)
- [[karar_r_max_dinamik_turetme]] (R10/RC10 için önceki en iyi kayıtlar, §9.0)
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]] (Ö1'in `src/`'deki öncülü, A5)
- [[solution_validator_fonksiyonlari]]
- [[degisken_z_arac_ekip_atama]]
- [[uyumluluk_matrisi]]
