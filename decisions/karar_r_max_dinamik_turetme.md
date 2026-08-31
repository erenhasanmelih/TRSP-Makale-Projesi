---
title: Karar (UYGULANDI) — R_max'ın Veriden Türetilmesi (birleştirme baskınlığı + zaman bütçesi)
tags: [karar, uygulandi, r-max, klon-dugum, coklu-sefer, olcek, mip-formulasyon, cv, ev]
source: raw/xml_data_loader.py; raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py
date: 2026-08-24
status: güncel
---

# Karar (UYGULANDI) — `R_max`'ın Veriden Türetilmesi

> **Durum: UYGULANDI (2026-08-24).** `raw/xml_data_loader.py` içine
> `derive_r_max()` + `max_single_trip_distance()` eklendi; `data['R_max']`
> hem CV hem EV modeline taşınıyor.
> Bu sayfa, [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] §8.3'te
> "yapılması gereken" olarak bırakılan ve §13.2.1'de **operasyonel gereklilik**
> ilan edilen mitigasyonun gerçekleştirimidir.

## 1. Çözülen sorun

Depo klon tasarımı `R_max` sefer klonu üretir: `2·R_max` düğüm, `2·R_max·n`
depo yayı, `R_max·|K|` adet `u[r,k]` değişkeni ve `R_max` kat CV-23/24,
CV-29/30/31 kısıtı. `R_max` sabit `3` iken bu, RC13 (EV, `|C|=13`, istasyonlu)
örneğinde 600 s'de **hiç fizibil çözüm bulunamamasına** yol açmıştı
([[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] §13.2.1).

Soru: `R_max`, **optimal çözümü kesmeden** veriden düşürülebilir mi?

## 2. §8.3'ün önerdiği formül YETERSİZDİR (bu sayfanın ilk bulgusu)

§8.3 şunu öneriyordu:

> `2·(min gidiş-dönüş süresi + min hizmet süresi) > ls − es` ise `R_max = 1`.

Bu formül mevcut veri setinde **hiçbir örnekte tetiklenmez**. Ölçülen değerler
(`raw/xml_data_loader.py`'nin ürettiği `tt`/`st` ile, **30 örnek** =
`raw/trsp_problem_sets/*.xml`'in tamamı):

| büyüklük | değer aralığı |
|---|---|
| `f_min = min_j (tt[0,j] + st_j + tt[j,0])` | **1060.2 – 1739.9 s** |
| vardiya penceresi `ls − es` | **32400 s** (9 saat) |
| `⌊(ls−es) / f_min⌋` | **18 – 30** |

Yani vardiya, en iyimser tek-müşterilik sefere göre 18-30 sefer alabilecek
kadar uzundur; zaman tabanlı sayım argümanı `min(3, ...)` sınırını hiç
düşürmez. **§8.3'ün önerdiği mitigasyon bu veri için geçersizdir.**
(Bu, tasarım sayfasının bir hatası değil, doğrulanmamış bir tahminidir —
sayfada da "örn." ibaresiyle verilmişti.)

## 3. Geçerli argüman: BİRLEŞTİRME BASKINLIĞI (merge dominance)

Asıl indirimi sağlayan argüman zaman sayımı değil, bir **baskınlık
(dominance) teoremidir**.

**Teorem.** Aynı kaynağın (`k = (v,t)`) ardışık iki seferi
`… → i → depo → j → …`, tek sefere birleştirildiğinde (`… → i → j → …`)
amaç fonksiyonu kötüleşmez ve **enerji dışındaki tüm kısıtlar korunur**.

*Kanıt taslağı (kısıt kısıt, `raw/CV_model_gurobi_exact.py` numaralarıyla):*

| Kısıt | Neden bozulmaz |
|---|---|
| Amaç (CV-1) | `d(i,j) ≤ d(i,0) + d(0,j)` — haversine bir metriktir (`raw/xml_data_loader.py:35-42`) |
| CV-2 | müşteri kümesi ve atamalar aynı kalır |
| CV-3 (yay tekilliği) | `i`, `j` müşteri ise CV-2 gereği onları ziyaret eden **tek** kaynak zaten `k`'dir → `(i,j)` yayını başka kaynak kullanamaz |
| CV-4a/b/c/d | `u[r+1,k]=0`, sonraki seferler bir aşağı kaydırılır; klon parametreleri takma ad olduğundan mesafe/süre değişmez |
| CV-5 | `i`'nin çıkan yayı `E_r` yerine `j`, `j`'nin giren yayı `O_{r+1}` yerine `i` — denge korunur |
| CV-8 zaman ilerlemesi | mevcut `τ` değerleri aynen geçerli: `τ_i + st_i + tt(i,0) ≤ τ[E_r] ≤ τ[O_{r+1}] ≤ τ_j − tt(0,j)` (CV-8, CV-29, CV-31) ve `tt(i,j) ≤ tt(i,0)+tt(0,j)` |
| CV-10/12/13 mola | mola kaldırılan yaylardan birindeyse yeni `(i,j)` yayına taşınır; `τ_i+st_i ≤ el` ve `τ_j ≥ ll` yukarıdaki zincirden türer. Mola **sayısı** değişmez → CV-13 `≤ z` / EV-12 `== z_veh` bozulmaz |
| CV-14 | `i` artık dönüş düğümü değil → kısıt gevşer; yeni dönüş düğümü zaten sağlıyordu |
| CV-15/16/18 | `τ` değerleri değişmedi |
| CV-19…CV-25 | **TEK İSTİSNA — bkz. §4** |

Şarj istasyonu ayrıntısı (EV): birleştirilen uçlardan biri istasyonsa o
istasyon w.l.o.g. rotadan atılabilir (depodan tam şarjla çıkıp hemen şarj
olmak veya şarj olup hemen depoya dönmek hem mesafeyi hem süreyi artırır),
dolayısıyla her iki uç da müşteri kabul edilebilir ve CV-3/EV-3 argümanı
geçerli kalır.

## 4. Tek engel enerjidir — ve ölçülebilir

Birleşen rota depoda **yeniden dolum yapmaz**: CV-23/24
(`raw/CV_model_gurobi_exact.py:556-570`) ve EV-24/25
(`raw/EV_v.1.1.py:560-574`) tam dolumu yalnızca **depodan çıkış yayında**
verir; ara düğümlerde dolum yasaktır (CV-22 `YC[i]==yc[i]`, EV-27).

Dolayısıyla:

> **Bir vardiyaya sığabilen HER rotanın uzunluğu araç menzilinden küçükse,
> enerji hiçbir zaman bağlamaz ⇒ her optimal çözüm kaynak başına TEK sefere
> indirgenebilir ⇒ `R_max = 1` optimal değeri KORUR.**

`max_single_trip_distance()` (`raw/xml_data_loader.py`) bu "vardiyaya sığan
en uzun rota" için iki bağımsız üst sınırın kesişimini, ziyaret edilen
müşteri sayısı `k` üzerinde maksimize ederek hesaplar:

```
(a) ZAMAN  : mesafe ≤ hız · ( bütçe − Σ_{en küçük k hizmet süresi} )
(b) YAY    : mesafe ≤ (en uzun k+1 yayın toplamı)        [k müşterili rota
                                                          TAM k+1 yay kullanır]
maxdist = max_k  min( (a), (b) )
```

(b) yalnızca rotada müşteri+depo dışında düğüm yoksa geçerlidir; bu yüzden
CV'de `arc_count_exact=True`, EV'de (şarj istasyonları nedeniyle)
`arc_count_exact=False` verilir ve EV yalnızca (a)'yı kullanır.

Bütçe: `ls−es` eksi **zorunlu** mola (`ll−el`). EV'de mola zorunludur
(EV-12 `== z_veh`), CV'de opsiyoneldir (CV-13 `≤ z`) → CV'de düşülmez.

### 4.1 Sayısal sonuç — testin ikisi de geçiyor

| | CV | EV |
|---|---|---|
| hız | 46.67 km/sa = 12.96 m/s | 37.5 km/sa = 10.42 m/s |
| bütçe | 32400 s (mola opsiyonel) | 32400 − 7200 = **25200 s** (mola zorunlu) |
| menzil | `G/h_c` = 6000/0.055 = **109 091 m** | `Q/h_e` = 50000/0.15528 = **322 000 m** |
| kaba zaman sınırı (`hız·bütçe`, hizmet süresi düşülmeden) | 420 036 m ✗ (menzili aşar) | 262 500 m ✓ (menzilin altında) |
| kodun ürettiği `maxdist` (30 örnek) | **11 292 – 81 479 m** ✓ (yay sınırı devrede) | **247 188 – 253 115 m** ✓ (yalnız zaman sınırı) |
| türetilen `R_max` | **1** (30/30 örnek) | **1** (30/30 örnek) |

EV'de kritik terim **zorunlu moladır**: molasız bütçe ile
`10.42 × 32400 = 337 500 m > 322 000 m` olur ve test geçmezdi. Yani
[[celiski_ogle_molasi_zorunlulugu]]'nda EV lehine kapatılan "mola zorunlu"
kararı, burada dolaylı bir ölçek kazancına dönüşmüştür.

CV'de ise **yay sayısı sınırı** kritiktir: yalnızca zaman sınırıyla test
geçmez (420 km > 109 km). En dar marj R100'de: 81 479 m / 109 091 m = **%74.7** (EV'de en dar marj
RC100'de: 253 115 m / 322 000 m = %78.6).
Yani test veri-bağımlıdır, sabit bir "her zaman 1" kuralı değildir — daha
seyrek/uzak müşteri dağılımı veya daha küçük depo (`Range`) `R_max=3`'ü geri
getirir.

## 5. Yedek argüman: zaman bütçesi (stage 2)

Birleştirme testi geçmezse `derive_r_max` §2'deki sayım argümanına düşer:
her sefer en az bir müşteri içerir, müşteri `j` içeren seferin süresi en az
`f_j = tt(0,j)+st_j+tt(j,0)`'dır (kapalı tur ≥ gidiş+dönüş), seferler CV-29
zinciriyle ardışıktır ve müşteri kümeleri ayrıktır ⇒ **en küçük `R` adet
`f_j`'nin toplamı bütçeye sığmalıdır**. Sonuç `[1, 3]` aralığına kırpılır
(`cap=3`, matematiksel modelin kendi CV-4/EV-4 sınırı; alt sınır 1 çünkü
"hiç çıkma" seçeneği zaten `z[k]=0` ile temsil edilir).

Bu yol mevcut veride hiç tetiklenmez ama **h_c/h_e veya menzil değişirse**
(örn. `EnergyConsumptionRate` XML'den okunamayıp `h_c=1.0` yedeğine düşerse,
`raw/xml_data_loader.py:260-262`) devreye girer ve model `R_max=3`'e güvenli
biçimde geri döner.

## 6. Global mi, kaynak-spesifik mi? — İKİSİ DE

- **Global `R_max`** = `max_t R_max(t)`. Klon kümesinin (`O`, `E`) boyutunu
  belirler; **değişken ve kısıt sayısını doğrudan azaltan** budur.
- **Kaynak-spesifik `R_max_by_tech`** = ekip bazlı değer. Klon kümesi
  küçültülemediğinde fazla klonlar `u[r,k].UB = 0` ile kapatılır
  (`raw/CV_model_gurobi_exact.py`, `raw/EV_v.1.1.py`, `u` tanımının hemen
  altındaki blok); Gurobi presolve bağlı `x`/`τ` değişkenlerini eler.

Mevcut veride `es`/`ls` tüm ekipler için aynıdır
(`raw/xml_data_loader.py`, `es_map`/`ls_map`), dolayısıyla ikisi eşittir ve
`u.UB=0` bloğu hiçbir şey yapmaz. Blok yine de bırakılmıştır: heterojen
vardiya penceresi eklendiğinde otomatik devreye girer ve **sağlamlığı
bozmaz** (her ekip kendi kanıtlanmış üst sınırıyla sınırlanır).

## 7. Uygulama — dokunulan yerler

**`raw/xml_data_loader.py`**

| Ekleme | Not |
|---|---|
| `max_single_trip_distance(d, st, customers, speed_ms, time_budget, arc_count_exact)` | §4'teki iki sınırın kesişimi |
| `derive_r_max(d, tt, st, C, es, ls, el, ll, speed_kmh, range_m, break_is_mandatory, cap, arc_count_exact)` | `(r_max, by_tech, info)` döner |
| `prepare_cv_data_from_instance` | `range_m = min(G)/h_c`, `break_is_mandatory=False`, `arc_count_exact=True` |
| `prepare_ev_data_from_instance` | `range_m = min(Q)/h_e`, `break_is_mandatory=True`, `arc_count_exact=False` |
| her iki `data` sözlüğü | yeni anahtarlar: `R_max`, `R_max_by_tech`, `R_max_info` |

**`raw/CV_model_gurobi_exact.py`** — `build_model` imzasına
`R_max_by_tech=None, R_max_info=None` eklendi (dikkat: `build_model(**data)`
ile çağrıldığı için `data`'ya eklenen HER anahtarın bir kwarg karşılığı
olmalıdır, aksi hâlde `TypeError`); `R_max = max(1, int(R_max))`;
`u[r,kk].UB = 0` bloğu; `m._R_max`, `m._R_max_info`; `__main__` içinde
türetim gerekçesini yazan bir `print`.

**`raw/EV_v.1.1.py`** — birebir simetrik (`data.get("R_max")`,
`data.get("R_max_by_tech")`, `model._R_max`).

## 8. SAĞLAMLIK KANITI — küçük örneklerde objektif DEĞİŞMEDİ

`raw/solution_validator.validate_solution()` ile, koşucular `raw/` dışında
(`%TEMP%\trsp_klon_test\run_cv.py`, `run_ev.py`, `ab_rmax.py`).
`MIPGap=0`, `TimeLimit=600 s`.

| Örnek | Model | `R_max=3` (eski) | türetilmiş `R_max=1` | aynı mı? |
|---|---|---|---|---|
| C5 | CV | 8291.2 (opt, 37.8 s) | **8291.2** (opt, 34.1 s) | ✔ |
| R5 | CV | 10116.1 (opt, 32.3 s) | **10116.1** (opt, 30.6 s) | ✔ |
| RC5 | CV | 7933.0 (opt, 31.8 s) | **7933.0** (opt, 31.0 s) | ✔ |
| C5 | EV | 8291.2 (gap %20.7) | **8291.2** (gap %16.6) | ✔ |
| R5 | EV | 10116.1 (opt, 126.2 s) | **10116.1** (opt, 124.2 s) | ✔ |
| RC5 | EV | 7933.0 (opt, 94.9 s) | **7933.0** (opt, 83.6 s) | ✔ |

Altı koşumun tamamında `valid=True` ve objektif **birebir aynı**. CV'de
üçü de kanıtlanmış optimal olduğundan bu, `R_max=1`'in optimal çözümü
kesmediğinin ampirik doğrulamasıdır (teorik kanıt §3-4).

## 9. MODEL BOYUTU KAZANCI

| Model | Örnek | `NumVars` | `NumConstrs` | `NumNZs` |
|---|---|---|---|---|
| CV | C5/R5/RC5 | 3502 → **2114** (%-39.6) | 9787 → **7067** (%-27.8) | 39628 → **26248** (%-33.8) |
| EV | C5/R5/RC5 | 8760 → **6412** (%-26.8) | 23183 → **18527** (%-20.1) | 82888 → **64768** (%-21.9) |

Bu, [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] §8'in
"klonlama maliyeti" tablosunun **tersine çevrilmiş** hâlidir: `R_max=1`,
klon tasarımının maliyetsiz sınır durumudur (depo yayları çoğaltılmaz),
buna karşılık CV-29/30/31'in getirdiği sefer-sırası doğruluğu korunur.

Küçültme oranı `n` büyüdükçe azalır (klonlanan yaylar toplam yayların
`O(n)/O(n²)`'sidir, §8'in analiziyle tutarlı): RC13'te (`|C|=13`, `|S|=4`,
`|K|=45`) `NumVars` 35821 → **29423** (%-17.9), `NumConstrs` 105168 →
**93850** (%-10.8), `NumNZs` 384101 → **335831** (%-12.6).

## 9.0 Orta boy örnekler (R10, RC10) — objektif aynı, ALT SINIR iyileşti

`TimeLimit=600 s`, `NoRelHeurTime=60 s`, `MIPGap=0.05`; hepsi `status=9`
(zaman limiti), hepsi `valid=True`.

| Örnek | Model | `R_max=3` obj / gap | `R_max=1` obj / gap | not |
|---|---|---|---|---|
| R10 | CV | 14335.3 / %32.4 | **14335.3** / **%25.8** | objektif aynı, gap **−6.6 puan** |
| RC10 | CV | 10588.4 / %34.7 | **10588.4** / **%32.4** | objektif aynı, gap −2.3 puan |
| R10 | EV | 14335.3 / %43.3 | 14393.6 / **%41.1** | incumbent %+0.4 kötü (ikisi de optimal değil), gap −2.2 puan |
| RC10 | EV | 14727.5 / %62.6 | **13899.5** / **%58.0** | incumbent **%-5.6 daha iyi**, gap −4.6 puan |

Model boyutu (R10, `\|K\|=30`): CV `NumVars` 9662 → **7074** (%-26.8),
EV 17320 → **13772** (%-20.5).

Asıl ve **tutarlı** kazanç alt sınırdadır: dört koşumun **dördünde de** gap
düştü (−6.6, −2.3, −2.2, −4.6 puan), çünkü küçülen dal-sınır ağacı aynı
sürede daha yüksek bir alt sınıra ulaşıyor. Incumbent tarafı karışıktır:
CV'de birebir aynı, EV RC10'da %5.6 daha iyi, EV R10'da %0.4 daha kötü
(hiçbiri optimal değil, dolayısıyla incumbent farkları **gürültüdür** —
karşılaştırılabilir olan büyüklük gap'tir).

> **Yan gözlem (2026-08-25):** EV R10 `R_max=1` koşumu, wiki kaydındaki **ilk
> gerçek şarj istasyonu ziyaretini** üretti (`ziyaret edilen istasyonlar=[11, 12]`).
> [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] §13.7 "hiçbir
> istasyon ziyaret edilmedi" sınırlaması böylece kısmen kapandı. Bu, §4'teki
> "enerji bağlamıyor" tespitiyle çelişmez: istasyon ziyareti *zorunlu* değil,
> yalnızca *mümkün*dür ve bu koşumda %41 gap'li bir ara çözümde mesafeyi
> boşuna artırmaktadır.

## 9.1 RC13 — HIZ KAZANCI DOĞRULANAMADI (dürüst negatif sonuç)

RC13 (EV, istasyonlu) bu çalışmanın hedef örneğiydi
([[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] §13.2.1: "`R_max=3`
600 s'de hiç fizibil çözüm bulamadı, `R_max=1` buldu"). **Bu gözlem yeniden
üretilemedi.** Dört koşum (`MIPGap=0.05`, `MIPFocus=1`):

| `TimeLimit` | `NoRelHeurTime` | `R_max=3` | türetilmiş `R_max=1` |
|---|---|---|---|
| 1500 s | 500 s | `obj=20753.8`, gap %58.2, `valid=True` | **`obj=20753.8`**, gap %58.4, `valid=True` |
| 600 s | 60 s | `obj=21214.3`, gap %59.7, `valid=True` | **`solcount=0`** (fizibil çözüm yok) |

Yorum:

1. **1500 s'de objektif BİREBİR AYNI** (`20753.8`) — sağlamlığın RC13
   ölçeğindeki ampirik doğrulaması. Gap farkı (%58.2 vs %58.4) ölçüm
   gürültüsüdür; alt sınır (kök LP) `R_max`'tan neredeyse etkilenmiyor.
2. **600 s'de yön TERSİNE döndü**: bu kez `R_max=1` çözüm bulamadı,
   `R_max=3` buldu. Yani RC13'te fizibil çözüm bulma başarısı `R_max`'a
   değil, Gurobi'nin sezgisel şansına bağlıdır. §13.2.1'in tek koşuma
   dayanan "`R_max` mitigasyonu operasyonel bir gerekliliktir" çıkarımı
   bu ölçümlerle **desteklenmiyor**.
3. `R_max=1`'in RC13'te fizibil olduğu **kanıtlıdır**, çünkü `R_max=3`
   koşumlarının bulduğu çözümlerin ikisinde de `multitrip={}`, yani her
   kaynak zaten tek sefer yapıyor; o çözümler doğrudan `R_max=1` modelinin
   de fizibil çözümüdür. 600 s'lik `solcount=0`, infeasibility değil,
   sezgisel başarısızlıktır.
4. RC13'ün asıl darboğazı çoklu sefer değil, **%58'lik alt sınır boşluğudur**
   (zayıf LP gevşetmesi). Bu, `R_max` ile değil, kesme düzlemi / geçerli
   eşitsizlik / daha sıkı Big-M ile ele alınacak ayrı bir iştir.

**Sonuç:** `R_max` türetiminin ana kazanımı **model boyutu + alt sınır
kalitesidir**, çözüm süresi değil. Kazanç `n` ile azalıyor:

| ölçek | gap kazancı |
|---|---|
| `n=5` (C5 EV, 600 s) | %20.7 → %16.6 (−4.1 puan); RC5 EV 94.9 s → 83.6 s |
| `n=10` (4 koşum, 600 s) | −6.6 / −2.3 / −2.2 / −4.6 puan (§9.0) |
| `n=13` + istasyon (RC13 EV, 1500 s) | %58.2 → %58.4 (**kazanç yok**) |

RC13'te kazancın kaybolması §8'in analiziyle tutarlıdır: klonlanan yaylar
toplam yayların `O(n)/O(n²)`'sidir, dolayısıyla `R_max` indirimi `n`
büyüdükçe modele daha az dokunur (RC13'te `NumVars` yalnızca %-17.9).

## 10. Sınırlamalar / ertelenenler

- Test **veri-bağımlıdır**: CV'de en dar marj %75 (R100). Menzil düşer,
  müşteriler uzaklaşır veya vardiya uzarsa `R_max` otomatik olarak 3'e
  döner — bu bir hata değil, tasarımın amacıdır.
- **Çoklu sefer mekanizması ölü değildir.** `R_max=1` bu *veri seti* için
  optimal-koruyucudur; kod yolu (CV-4a..d, CV-29/30/31, `u[r,k]`) olduğu
  gibi durur ve `data['R_max']` elle 3 yapılarak geri açılabilir. Bu,
  [[celiski_single_trip_vs_multitrip]]'te kapatılan docx↔kod çelişkisini
  **yeniden açmaz**: model hâlâ çoklu sefer modelidir, yalnızca bu veride
  kanıtlanabilir biçimde gereksizdir.
- `R_max_by_tech` yolu mevcut veride vakumdadır (homojen `es`/`ls`);
  gerçek ampirik testi yapılmamıştır.
- Birleştirme teoreminin §3'teki kanıtı **kısıt-kısıt elle** yürütülmüştür;
  biçimsel (makine ile doğrulanmış) bir kanıt yoktur.

## Sources

- `raw/xml_data_loader.py` — `max_single_trip_distance`, `derive_r_max`,
  `prepare_cv_data_from_instance`, `prepare_ev_data_from_instance`
- `raw/CV_model_gurobi_exact.py` — `build_model` imzası, `R_max` bloğu,
  `u[r,kk].UB` bloğu, CV-22/23/24/25 (enerji), CV-29/30/31
- `raw/EV_v.1.1.py` — `R_max` bloğu, `u[r,kk].UB` bloğu, EV-24/25/26/27
- `raw/FC_Info4Vehicle4CV.xml` (`Range=6000`, `EnergyConsumptionRate=0.055`,
  `MaxSpeed=46.67`), `raw/FC_Info4Vehicle4EV.xml` (`BatteryCapacity=50000`,
  `Range=322000`, `MaxSpeed=37.5`)
- [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] §8.3, §13.2.1

## Related

- [[karar_rc13_asgari_paket_uygulamasi]] (R10/RC10'un burada §9.0'da kayıtlı gap'li en iyi bilinen değerleri artık kanıtlanmış optimalle değiştirildi, RC10 EV'de yeni bir en iyi değer bulundu)
- [[sorun_rc13_darbogaz_kok_neden_analizi]] (§9.1'in çıkış noktası, RC13'ün gerçek kök nedenini doğrular)
- [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]]
- [[klon_dugum_node_replication]]
- [[celiski_single_trip_vs_multitrip]]
- [[celiski_ogle_molasi_zorunlulugu]]
- [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]
- [[tight_big_m]]
- [[solution_validator_fonksiyonlari]]
