---
title: Sorun (TEŞHİS) — RC20 "0 Çözüm"ün Kök Nedeni: Model DARBOĞAZDA DEĞİL, INFEASIBLE
tags: [sorun, teshis, rc20, infeasibility, fizibilite, ekip-atama, sirt-cantasi, mola, ev-22, ev-23, cv-14, mip-formulasyon, ev, cv]
source: raw/EV_v.1.1.py; raw/CV_model_gurobi_exact.py; raw/Info4Employee.xml; raw/FC_Info4Vehicle4EV.xml; raw/trsp_problem_sets/RC20.xml
date: 2026-08-31
status: güncel
---

# Sorun (TEŞHİS) — RC20 Neden Hiç Çözüm Vermiyor

> **GÜNCELLEME (2026-08-31): §5'teki "Ö-A: tam kadro" seçeneği `raw/`'a
> UYGULANDI** — bkz. [[karar_5_8_teknisyen_bug_fix]]. Bu, `skill_tech_map`
> hatasını (§2 madde 1) bir *bug fix* olarak düzeltir; Ö-B (filo 3→4),
> Ö-C (vardiya penceresi) ve Ö-D (n≥20'yi kapsam dışı bırakma) hâlâ
> **UYGULANMADI**, Eren'in açık talimatıyla RC20 üzerinde bu turda başka
> hiçbir işlem yapılmadı. Pratik sonuç (§5 tablosundan, önceden ölçülmüş):
> RC20 artık INFEASIBLE değil ama tam modelde 900 s'de hâlâ 0 çözüm veriyor
> — yani bu sayfanın §1 SONUCU ("RC20 ... INFEASIBLE'dır") **`raw/`'un
> düzeltme ÖNCESİ hâli için geçerliydi/geçerlidir**; düzeltme SONRASI hâlde
> RC20 artık infeasible değil, yalnızca (ayrıca) zor bir örnektir. §4.3'teki
> "n≤15" sınırının da bu bug fix ışığında yeniden değerlendirilmesi gerekir
> (n=20 taraması bug fix öncesi hâlle yapıldı) — bu **yapılmadı**, ileride
> ele alınacak açık bir iştir.
>
> **Bu diagnostik tur** (aşağıdaki §1-§8, 2026-08-31 ilk yazım) `raw/`
> DEĞİŞTİRİLMEDEN yapıldı (CLAUDE.md Hard Rule §7.1) — yukarıdaki güncelleme
> notu ayrı, sonraki bir onaylı adımdır. Tüm
> ölçümler `raw/` dışındaki bir teşhis koşucusuyla yapıldı
> (`%TEMP%\...\scratchpad\`: `harness.py`, `proof.py`, `scan.py`,
> `corroborate.py`, `corr_cv.py`, `whatif.py`, `whatif_roster.py`);
> koşucu `raw/EV_v.1.1.py` ve `raw/CV_model_gurobi_exact.py`'yi **import
> ederek** kullanır, kopyalamaz veya değiştirmez.
>
> Öncül: [[sorun_rc13_darbogaz_kok_neden_analizi]] (RC13'ün kök nedeni: LP
> gevşetmesinde depo bağlantısının hiç zorlanmaması) ve
> [[karar_rc13_tam_paket_uygulamasi]] §1/§9 ("RC20 300 s'de hâlâ 0 çözüm,
> alt sınır 24099.9'a yükseliyor"). Bu sayfa o gözlemin **teşhisini
> düzeltir**.

## 1. Sonuç önce — RC20 çözülemiyor değil, ÇÖZÜMÜ YOK

**RC20 (hem EV hem CV) mevcut `raw/` konfigürasyonunda MATEMATİKSEL OLARAK
INFEASIBLE'dır.** Gurobi'nin 180/300/1800 s'de "0 çözüm" vermesi bir arama
gücü / formülasyon zayıflığı sorunu **değildir**; fizibil çözüm kümesi
**boştur**. Alt sınırın 24099.9'a "yükselmesi" de bir yakınsama değil,
infeasibility'nin B&B ağacında yavaşça ortaya çıkışıdır (her düğüm
`infeasible` olarak kapanıyor, alt sınır +∞'a doğru sürünüyor).

| Model | Ek kısıt | Gurobi durumu | Süre |
|---|---|---|---|
| `raw/` RC20 EV (değiştirilmemiş, `MIPFocus=3`) | — | `TIME_LIMIT` (9), **SolCount=0**, bound **25 144.16**, 569 287 düğüm | 1800 s |
| `raw/` RC20 CV (değiştirilmemiş, `MIPFocus=1`) | — | `TIME_LIMIT` (9), **SolCount=0**, bound **18 393.08**, 563 979 düğüm | 1800 s |
| `raw/` RC20 EV + **1 geçerli eşitsizlik** | §4 | **`INFEASIBLE` (3) — KANITLANDI** | **2.5 s** |
| `raw/` RC20 CV + **aynı geçerli eşitsizlik** | §4 | **`INFEASIBLE` (3) — KANITLANDI** | **8.0 s** |

Aynı geçerli eşitsizlik RC13/RC15/R15/C15'te **bilinen optimalleri
değiştirmez** (§4.2) — yani eşitsizlik hiçbir fizibil çözümü kesmiyor,
dolayısıyla RC20'nin infeasibility'si **orijinal modelin kendi
özelliğidir**.

## 2. Kök neden — beceri→ekip bölünmesi ile günlük kapasite çakışıyor

Zincir beş halkadan oluşur; hepsi mevcut kodun/verinin doğrudan sonucudur:

1. **Yalnızca 5 teknisyen aktifleştiriliyor.** `raw/Info4Employee.xml`'de
   **8 teknisyen** var (`s1→[TECH_001, TECH_002]`, `s2→[TECH_003, TECH_004]`,
   `s3→[TECH_005, TECH_006]`, `s4→[TECH_007]`, `s5→[TECH_008]`), ama
   `raw/EV_v.1.1.py:1188` ve `raw/CV_model_gurobi_exact.py:1087` her
   beceriden **yalnızca ilkini** alır:
   ```python
   tech = skill_tech_map[skill][0]
   ```
   → aktif teknisyenler `{TECH_001, TECH_003, TECH_005, TECH_007, TECH_008}`;
   `TECH_002 / TECH_004 / TECH_006` **hiç kullanılmıyor**. `T` bu 5
   teknisyenin tekilleri + ikilileri = `5 + C(5,2) = 15` ekiptir.
2. **En fazla 3 ekip aynı anda aktif.** EV-22 (`raw/EV_v.1.1.py:446-449`,
   agregat mod: `Σ_t z_veh[t] ≤ |V|`) / CV-27 (`:355-359`); filo
   `raw/FC_Info4Vehicle4EV.xml`'de **3 araç** (`EV_1..EV_3`, birebir aynı).
3. **Bir teknisyen en fazla 1 aktif ekipte.** EV-23 (`:458-473`) /
   CV-28 (`:368-388`).
4. → **{2,2,1} bölünmesi ZORUNLU.** 5 beceriyi ≤3 ekiple kapatmak, her ekip
   ≤2 teknisyen içerdiği için ancak 2+2+1 ile mümkündür (3 ikili 6 farklı
   teknisyen isterdi, elde 5 var). Bir becerinin **tüm** müşterileri, o
   beceriye sahip **tek** aktif ekibe düşer (EV-2 `:397-402` / CV-2
   yetkinlik kısıtı) — yani beceri bazlı yükler **bölünemez atomlardır**.
5. **Aktif kaynak başına günlük hizmet kapasitesi 25 200 s.** EV-12
   (`:647-651`, `Σ w[i,j,kk] == z_veh[kk]`) her aktif kaynağa **tam bir**
   mola dayatır; EV-9 (`:598-607`)
   mola öncesi bitişi `el`'e, EV-11 (`:620-627`) mola sonrası varışı `ll`'ye
   bağlar; EV-7 mola terimini `w·(ll−el)` olarak zaman ilerlemesine **ekler**
   (seyahat mola içinde emilmez). Dolayısıyla aktif her kaynak için
   ```
   Σ st_i + Σ tt_ij + (ll − el) ≤ ls − es
   ⇒ Σ st_i ≤ (ls − es) − (ll − el) = 32400 − 7200 = 25 200 s
   ```

### 2.1 Rakamlar — RC20 bu duvarı 791 saniyeyle aşıyor

RC20'de beceri bazlı toplam hizmet süreleri
(`raw/trsp_problem_sets/RC20.xml`):

| beceri | müşteri | toplam `st` (s) | zorunlu öğleden sonra | zorunlu sabah |
|---|---|---|---|---|
| s1 | 4 | 19 059 | 8 830 | 0 |
| s2 | 3 | 15 392 | 10 171 | 5 221 |
| s3 | 2 | 11 224 | 0 | 5 253 |
| s4 | 4 | 10 599 | 0 | 3 543 |
| s5 | 7 | 12 466 | 2 902 | 6 278 |
| **TOPLAM** | **20** | **68 740** | 21 903 | 20 295 |

15 adet `{2,2,1}` bölünmesinin **15'i de** en az bir grupta 25 200 s'i aşar:

| bölünme | grup yükleri (s) | max | durum |
|---|---|---|---|
| **s2+s4 \| s3+s5 \| s1** | [25 991, 23 690, 19 059] | **25 991** | **ihlal (+791 s)** |
| s2+s3 \| s4+s5 \| s1 | [26 616, 23 065, 19 059] | 26 616 | ihlal |
| s2+s5 \| s3+s4 \| s1 | [27 858, 21 823, 19 059] | 27 858 | ihlal (ayrıca PM 13 073 > 10 800) |
| s1+s4 \| … | [29 658, …] | 29 658 | ihlal |
| s1+s3 \| … | [30 283, …] | 30 283 | ihlal |
| s1+s5 \| … | [31 525, …] | 31 525 | ihlal |
| s1+s2 \| … | [34 451, …] | 34 451 | ihlal |

**En iyi olası bölünme kapasiteyi yalnızca 791 s (13,2 dakika) aşıyor** — ve
bu, **hiç seyahat süresi sayılmadan** elde edilen bir alt sınırdır. Her
müşterinin minimum giren seyahat süresi eklendiğinde en iyi max grup
26 144 s'ye çıkar (aşım 944 s).

Karşılaştırma (aynı hesap): RC13 → 19 059 s (kapasitenin %75,6'sı, 6/15
bölünme fizibil), RC15 → 19 059 s (%75,6, 6/15 fizibil). **Duvar, 15 ile 20
müşteri arasındadır.**

### 2.2 CV de aynı duvara çarpıyor — CV-14 yüzünden

CV'nin molası **opsiyoneldir** (CV-13, `raw/CV_model_gurobi_exact.py:565-569`:
`Σ w ≤ z`), bu yüzden ilk bakışta bir CV ekibi molayı atlayıp tüm
`ls − es = 32 400` s'yi kullanabilirmiş gibi görünür — ki o zaman
`s1+s2` hariç bölünmeler geçerdi. Ama **CV-14 (MOLASIZ ERKEN DÖNÜŞ,
`:571-590`)** molayı kullanmayan kaynağı `ll`'ye kadar depoya dönmeye
zorlar:

```
τ_i + st_i + tt_i0 ≤ ll + (ls−ll)·(1 − ret_i + Σw)      # CV-14
Σw = 0, ret_i = 1  ⇒  τ_i + st_i + tt_i0 ≤ ll = 21 600
```

Yani CV'de kapasite:
- mola **var** → `Σst ≤ (ls−es) − (ll−el) = 25 200`
- mola **yok** → `Σst ≤ ll − es = 21 600` (**daha da dar**)

→ her iki dalda `Σst ≤ 25 200`; EV ile **aynı** duvar. Bu yüzden CV RC20 da
infeasible (§1 tablosu, 8.0 s'de kanıtlandı).

> **Not:** İlk gevşetme denemem CV'yi molasız modda 32 400 s kapasiteyle
> modellemiş ve "fizibil" demişti; CV-14 okununca bu düzeltildi. CV'nin
> mola opsiyonelliğinin **kapasite avantajı yaratmadığı**, ayrıca
> belgelenmesi gereken bir sonuçtur — bkz. [[celiski_ogle_molasi_zorunlulugu]]
> ve [[karar_molasiz_erken_donus_kurali_kod]].

## 3. Hipotezlerin değerlendirmesi

| Hipotez (görev tanımından) | Karar | Kanıt |
|---|---|---|
| **H1 — Ölçek etkisi** (aynı RC13 patolojisi, sadece daha büyük; süre yetersiz) | **KÖK NEDEN OLARAK ÇÜRÜTÜLDÜ, ikincil etken olarak DOĞRULANDI** | 1800 s'de hâlâ 0 çözüm ve model infeasible (§1). Ancak infeasibility giderildiğinde (|V|=4) bile 900 s'de yalnızca %9,35 gap'e inilebiliyor (§5) → RC20 **ayrıca** zor |
| **H2 — Fizibilite sınırı** (mola + TW bin-packing filo kapasitesini aşıyor) | **DOĞRULANDI ve AŞILDI** | Sadece "sınırda" değil, sınırın **ötesinde**: en iyi bölünme kapasiteyi 791 s aşıyor (§2.1). RC13'teki `min_veh` argümanının aynı ailesinden ama **beceri→ekip** ekseninde |
| **H3 — RC13'te olmayan yeni yapısal darboğaz** | **DOĞRULANDI** | Yeni eksen: **beceri bazlı yükün bölünemezliği** (EV-2 + EV-23). RC13/RC15'te 6/15 bölünme fizibil, RC20'de **0/15** (§2.1). RC13'ün `min_veh` kesiti bu ekseni hiç görmüyor (sefer sayısına bakıyor, ekip kompozisyonuna değil) |
| **H4 — Gerçekten infeasible** | **DOĞRULANDI** | §1 + §4; tam sayım (§2.1) + gevşetme MIP/IIS (§4.1) + Gurobi kanıtı (§4.2) — üç bağımsız yöntem |
| İstasyon sayısı/konfigürasyonu | **KONUSUZ** | Ö6 gereği `S = []` (`stations_dropped=True`), RC13 ile aynı |
| Mesafe ölçeği | **ÇÜRÜTÜLDÜ** | Toplam seyahat bütçesi (6 860 s) minimum seyahatin (796 s) 8,6 katı; darboğaz mesafe değil (§2.1) |

## 4. Kanıt yöntemleri

### 4.1 Gevşetme MIP + IIS (rotalama tamamen atılmış)

Rotalamayı, zamanı ve mesafeyi **tamamen** atan bir atama MIP'i kuruldu
(yalnızca `z[t]`, `y[i,t]`, sabah/öğleden-sonra parçası; kısıtlar: kapsama,
EV-22, EV-23, AM/PM kapasiteleri, zorunlu AM/PM). Bir gevşetme infeasible
ise **tam model de infeasible'dır**.

| Örnek | Gevşetme | Aktif ekipler (fizibilse) |
|---|---|---|
| RC13 EV | **fizibil** | `TECH_008 \| TECH_001_TECH_007 \| TECH_003_TECH_005` |
| RC15 EV | **fizibil** | aynı |
| **RC20 EV** | **INFEASIBLE** | — (IIS: 76 kısıt; `fleet`×1, `tech`×5, `amcap`×8, `pmcap`×8, `cover`×17, `link`×31, `forcePM`×3, `forceAM`×1) |

### 4.2 Gurobi kanıtı — değiştirilmemiş `raw/` modeli + tek geçerli eşitsizlik

`raw/` modeline yalnızca şu eşitsizlik eklendi (`corroborate.py` / `corr_cv.py`):

```python
Σ_{(i,j) ∈ At}  st_i · x[i,j,kk]  ≤  25200 · z_veh[kk]      # her kk ∈ K
```

Geçerlilik §2-5'te (EV) ve §2.2'de (CV) türetildi. **Geçerlilik ampirik
olarak da doğrulandı** — aynı eşitsizlikle:

| Örnek | Model | Durum | `ObjVal` | Wiki'deki bilinen optimal |
|---|---|---|---|---|
| RC13 | EV | OPTIMAL (6.3 s) | **20 666.99** | 20 666.99 ✔ |
| RC15 | EV | OPTIMAL (4.6 s) | **23 912.82** | 23 912.82 ✔ |
| R15 | EV | OPTIMAL (9.7 s) | 12 704.58 | — (yeni) |
| C15 | EV | OPTIMAL (11.0 s) | 14 654.74 | — (yeni) |
| RC13 | CV | OPTIMAL (26.2 s) | **20 666.99** | 20 666.99 ✔ |
| RC15 | CV | OPTIMAL (13.5 s) | **23 912.82** | 23 912.82 ✔ |
| **RC20** | **EV** | **INFEASIBLE (2.5 s)** | — | — |
| **RC20** | **CV** | **INFEASIBLE (8.0 s)** | — | — |

Eşitsizlik hiçbir bilinen optimali kesmediğine göre, RC20'nin
infeasibility'si eşitsizliğin değil **modelin** özelliğidir.

### 4.3 Tarama — n ≥ 20 olan TÜM örnekler infeasible

Aynı argüman (`scan.py`) 30 örneğin hepsine uygulandı:

| Örnek grubu | `Σ st` (s) | en iyi bölünmede max grup (s) | kapasite | karar |
|---|---|---|---|---|
| C5/R5/RC5 | 15 891 | 6 146 | 25 200 | fizibil olabilir |
| C7 / R7 / RC7 | 20 450 / 27 811 / 23 164 | 8 427 / 12 537 / 12 537 | 25 200 | fizibil olabilir |
| C10/R10/RC10 | 35 213 | 12 537 | 25 200 | fizibil olabilir |
| C13/R13/RC13 | 42 455 / 46 360 / 45 694 | 15 817 / 17 217 / 19 059 | 25 200 | fizibil olabilir |
| C15/R15/RC15 | 49 876 / 53 679 / 53 580 | 19 360 / 19 985 / 19 059 | 25 200 | fizibil olabilir |
| **C20/R20/RC20** | **68 740** | **25 991** | 25 200 | **INFEASIBLE (kanıt)** |
| **C40/R40/RC40** | 153 946 | 57 042 | 25 200 | **INFEASIBLE** |
| **C60/R60/RC60** | 222 574 | 86 474 | 25 200 | **INFEASIBLE** |
| **C80/R80/RC80** | 302 235 | 111 731 | 25 200 | **INFEASIBLE** |
| **C100/R100/RC100** | 344 177 | 122 150 | 25 200 | **INFEASIBLE** |

**Mevcut `raw/` konfigürasyonunda exact modelin çözebileceği en büyük örnek
boyutu n = 15'tir.** 20/40/60/80/100'lük 15 örneğin tamamı (CV+EV) fizibil
çözüme sahip değildir. C20/R20/RC20'nin hizmet süreleri ve beceri dağılımı
**birebir aynıdır** (yalnızca koordinatlar farklı) — bu yüzden üçü de aynı
noktadan infeasible olur.

## 5. Ne düzeltirse RC20 fizibil olur (ölçüldü, UYGULANMADI)

Her seçenek yukarıdaki gevşetme MIP'iyle test edildi; ✔ işaretliler tam
model üzerinde de koşuldu.

| Seçenek | Neyi değiştirir | Gevşetme | Tam model (EV RC20, 900 s) |
|---|---|---|---|
| **Ö-A: tam kadro** — `skill_tech_map[skill][0]` yerine **tüm** teknisyenler | `\|T\|` 15 → 36; `NumVars` 11 924 → **28 556**, `NumConstrs` 31 361 → **74 666** | **fizibil** (`TECH_001_TECH_003 \| TECH_002_TECH_007 \| TECH_005_TECH_008`) | ✔ 900 s'de **hâlâ 0 çözüm** (alt sınır 20 852.6) — fizibiliteyi geri kazandırır ama model 2,4× büyüdüğü için pratikte çözüm üretmez |
| **Ö-B: filo 3 → 4** | `\|T\|` değişmez, model boyutu **aynı** | **fizibil** (`TECH_001 \| TECH_003 \| TECH_005 \| TECH_007_TECH_008`) | ✔ **9 çözüm bulundu**, ilk incumbent **246 s**, 900 s'de `ObjVal = 29 104.18`, gap **%9,35** |
| Ö-C: vardiya penceresi `ls` genişletme | kapasite `25 200`'ü büyütür | fizibil (≥ +791 s ile) | ölçülmedi |
| Ö-D: n ≥ 20'yi exact kapsamı dışına al | — | — | makale kararı (bkz. §7) |

**Ö-B en ucuz ve en etkili müdahaledir**: model boyutunu hiç büyütmez
(homojen filoda Ö2 agregasyonu nedeniyle `|V|` yalnızca
`Σ_t z_veh[t] ≤ |V|` sağ tarafında görünür, `raw/EV_v.1.1.py:446-449`) ve
RC20'yi "0 çözüm"den "%9,35 gap"e taşır. Ö-A modeli 2,4× büyüttüğü için
fizibiliteyi geri kazandırsa da pratikte çözüm üretmedi.

**Kritik uyarı:** bu seçeneklerin hiçbiri bir "hata düzeltmesi" değildir —
hepsi **problem tanımını değiştirir** (kaç teknisyen / kaç araç var?).
Hangisinin doğru olduğu bir **veri/senaryo kararıdır**, Eren'in onayı
gerekir. `raw/`'a hiçbir şey uygulanmamıştır.

## 6. ÇELİŞKİ — önceki tur RC20'yi "darboğaz" olarak teşhis etmişti

**İddia A** ([[karar_rc13_tam_paket_uygulamasi]] §1 ve §9, 2026-08-29;
aynı ifade `log.md`'de):
> "RC20 → 300 s'de **hâlâ 0 çözüm** (alt sınır 24099.9'a yükseliyor —
> Gurobi'nin varsayılan sezgiselleri bu ölçekte İLK fizibıl çözümü bile
> bulamıyor). Muhtemel sonraki adımlar: Ö5'in lazy-callback biçimi,
> warm-start (heuristic'ten ilk çözüm), veya yalnızca parametre taraması."

**İddia B** (bu sayfa, 2026-08-31):
> RC20 EV **ve** CV **infeasible**'dır (§1, §4). Hiçbir sezgisel, hiçbir
> warm-start, hiçbir kesme düzlemi ve hiçbir parametre ayarı fizibil çözüm
> **bulamaz** — çünkü fizibil çözüm yoktur.

**Karar: İddia A ÇÜRÜTÜLDÜ (teşhis hatası).** İddia A'nın *gözlemi*
(0 çözüm, alt sınır yükseliyor) doğrudur; *yorumu* (arama gücü yetersizliği)
yanlıştır. Yükselen alt sınır infeasibility'nin B&B'de yavaş ortaya
çıkışıdır. İddia A'nın önerdiği "Ö5 lazy-callback / warm-start / parametre
taraması" yolunun tamamı **boşa yatırım** olurdu.

Bu, [[karar_rc13_tam_paket_uygulamasi]] §9'daki "Sınırlamalar" maddesinin
ve `log.md`'nin 2026-08-29 girdisinin **düzeltilmesini gerektirir** —
CLAUDE.md Hard Rule §7.4 gereği hiçbir taraf silinmedi, her iki iddia da
kaynağıyla burada duruyor.

**İkincil not:** İddia A'nın rakamı (alt sınır 24 099.9 @ 300 s) bu turda
birebir tekrar edilemedi; 1800 s / `MIPFocus=3` koşumunda alt sınır 477 s'de
22 572, koşum sonunda **25 144.16**'ya ulaştı (569 287 düğüm, hâlâ 0 çözüm);
CV tarafında 1800 s / `MIPFocus=1` ile **18 393.08** (563 979 düğüm, 0 çözüm).
Parametre farkı (`MIPFocus`) beklenen bir sapmadır, sonucu (0 çözüm)
değiştirmez — ve alt sınırın 24 099.9'u **geçip** yükselmeye devam etmesi
§1'deki yorumu (`+∞`'a sürünme) ayrıca destekler: sonlu bir gap'e
yakınsamıyor, çünkü yakınsayacağı bir optimal yok.

## 7. Makale/rapor açısından sonuç

1. **`raw/sonuclar/` ve gelecek deney tablolarında RC20/R20/C20 ve n ≥ 40
   satırları "çözülemedi / time limit" olarak raporlanmamalıdır** —
   doğru etiket **"infeasible (mevcut kaynak konfigürasyonunda)"**dır.
   Bu iki şey bilimsel olarak tamamen farklı ifadelerdir.
2. **Exact model ile heuristic'in karşılaştırılabileceği örnek kümesi
   `n ≤ 15`'tir** (§4.3). Heuristic n ≥ 20'de "çözüm buluyor" görünüyorsa
   ya farklı bir kaynak konfigürasyonu kullanıyordur ya da bir kısıtı
   ihlal ediyordur — bu, exact↔heuristic karşılaştırma katmanına ait ayrı
   ve **acil** bir doğrulama işidir (sezgisel çözümler
   `raw/solution_validator.py` ile aynı kısıt kümesine karşı denetlenmeli).
3. Mevcut `raw/Info4Employee.xml`'deki **8 teknisyenin 3'ünün hiç
   kullanılmaması** (§2-1) muhtemelen istenmeyen bir veri hazırlama
   kısıtlamasıdır; makalede "8 teknisyenlik iş gücü" iddiası varsa bu bir
   **docx↔kod çelişkisi** adayıdır (henüz yönerge dokümanlarıyla
   karşılaştırılmadı).

## 8. Sınırlamalar / emin olunamayan noktalar

- Fizibilite argümanı `Σ st ≤ 25 200` **alt sınırına** dayanır; seyahat
  süresi sayılmadığı için **muhafazakârdır** (gerçek kapasite daha da
  dardır). Yani argüman yanlış yönde hata yapmaz.
- `Σ st ≤ 25 200` türetimi, tüm ekiplerin `es/ls/el/ll` değerlerinin aynı
  olmasına dayanır (mevcut veride öyle — `raw/EV_v.1.1.py:1208-1216` tüm
  ekiplere `all_technicians[0]`'ın penceresini kopyalıyor). Heterojen
  vardiyada tekrar türetilmelidir.
- Ö-A'nın (tam kadro) tam modelde çözüm üretememesi 900 s ve tek tohum
  (`Seed=1`) ile ölçüldü; daha uzun süre veya `Ö2` benzeri ek indirimlerle
  değişebilir.
- `min_veh` (Ö3) ve `bwp` (Ö4) kesitlerinin RC20'de infeasibility'ye
  **katkısı yoktur** — kanıt yalnızca EV-2/9/11/12/22/23 + veri hazırlamaya
  dayanır, Ö3/Ö4 kullanılmadan da geçerlidir.
- CV tarafında `Σ st ≤ 25 200` sınırının molasız dalı (`ll − es = 21 600`)
  CV-14'ün Big-M'inin doğru çalışmasına bağlıdır (`bigM = ls − ll`, sıkı —
  `raw/CV_model_gurobi_exact.py:578`).

## Sources

- `raw/EV_v.1.1.py:1188` (`skill_tech_map[skill][0]`), `:1192-1203` (ekip
  kurulumu), `:1208-1216` (vardiya penceresi kopyalama), `:439-449` (EV-22),
  `:458-473` (EV-23), `:598-607` / `:620-627` (EV-9/EV-11), `:647-651`
  (EV-12), `:397-402` (EV-2)
- `raw/CV_model_gurobi_exact.py:1087` (`skill_tech_map[skill][0]`),
  `:347-366` (CV-27), `:368-388` (CV-28), `:551-569` (CV-13 opsiyonel mola),
  `:571-590` (CV-14 molasız erken dönüş)
- `raw/Info4Employee.xml` (8 teknisyen, 5 beceri),
  `raw/FC_Info4Vehicle4EV.xml` / `raw/FC_Info4Vehicle4CV.xml` (3'er araç),
  `raw/trsp_problem_sets/RC20.xml` (20 müşteri, `Σ st = 68 740 s`)
- Teşhis koşucusu (`raw/` DIŞINDA): `%TEMP%\claude\...\scratchpad\`
  `harness.py`, `stats.py`, `budget.py`, `partition.py`, `proof.py`,
  `fullroster.py`, `cvrelax.py`, `scan.py`, `corroborate.py`, `corr_cv.py`,
  `whatif.py`, `whatif_roster.py`, `run.py`
- [[sorun_rc13_darbogaz_kok_neden_analizi]], [[karar_rc13_tam_paket_uygulamasi]]

## Related

- [[sorun_rc13_darbogaz_kok_neden_analizi]] (öncül teşhis — RC13'ün kök nedeni LP zayıflığıydı; RC20'ninki ondan **tamamen farklı** bir eksende)
- [[karar_rc13_tam_paket_uygulamasi]] (§1/§9'daki RC20 teşhisi bu sayfayla **çürütüldü**, bkz. §6)
- [[karar_rc13_asgari_paket_uygulamasi]]
- [[celiski_ogle_molasi_zorunlulugu]] (EV-12 zorunlu / CV-13 opsiyonel ayrımı — §2.2'de CV-14 nedeniyle kapasite açısından **fark yaratmadığı** gösterildi)
- [[karar_molasiz_erken_donus_kurali_kod]] (CV-14 — CV'nin mola opsiyonelliğini kapasite avantajına çevirmesini engelleyen kısıt)
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]] (`T = tekiller + ikililer` kurulumu; `[0]` seçimi burada belgeli)
- [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]] (EV-22/23, CV-27/28'in eklenme gerekçesi)
- [[karar_r_max_dinamik_turetme]]
- [[gurobi_mip_cozucusu]]
- [[uyumluluk_matrisi]]
