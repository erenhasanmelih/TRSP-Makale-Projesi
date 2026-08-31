---
title: Sorun (TEŞHİS) — RC13 Darboğazının Kök Nedeni: LP Gevşetmesinde Depo Bağlantısının Hiç Zorlanmaması
tags: [sorun, teshis, rc13, lp-gevsetmesi, altur-eleme, simetri, big-m, gecerli-esitsizlik, mip-formulasyon, ev, cv]
source: raw/EV_v.1.1.py; raw/CV_model_gurobi_exact.py; raw/xml_data_loader.py
date: 2026-08-27
status: güncel
---

# Sorun (TEŞHİS) — RC13 Darboğazının Kök Nedeni

> **GÜNCELLEME (2026-08-28): Ö1+Ö2+Ö6 UYGULANDI.** Eren'in onayıyla, §6'daki
> önerilerden Ö1+Ö2+Ö6 (+ `sorted(set(...))` düzeltmesi) doğrudan `raw/`'a
> işlendi — bkz. [[karar_rc13_asgari_paket_uygulamasi]]. **ÖNEMLİ DÜZELTME:**
> o sayfanın §1'i, aşağıdaki §6 giriş notundaki "asgari paket Ö1+Ö2+Ö6,
> 2.7 s'de kanıtlanmış optimal" iddiasının **YANLIŞ KARAKTERİZE EDİLDİĞİNİ**
> gösteriyor — 2.7 s rakamı Ö1+Ö2+Ö3+Ö4+Ö6+Ö7'nin (min_veh ve bwp+arc_fix
> DAHİL) birlikte sonucudur. Yalnızca Ö1+Ö2+Ö6 ölçüldüğünde gerçek sonuç
> RC13'te **~67-106 s'de kanıtlanmış optimal** (yine de raw/ eşdeğerinin
> 900 s'de 0 çözümüne karşı büyük bir kazanç). Bu bölümün geri kalanı,
> orijinal teşhis turunun (`raw/` dışı prototip) değişmemiş kaydıdır.
>
> Bu turda `raw/CV_model_gurobi_exact.py`, `raw/EV_v.1.1.py` ve
> `raw/xml_data_loader.py` **değiştirilmemiştir**. Tüm ölçümler `raw/`
> dışındaki bir prototip kopyada (`%TEMP%\rc13_diag\proto_ev.py`,
> `raw/EV_v.1.1.py`'nin anahtarlanabilir kopyası) yapılmıştır.
>
> Öncül: [[karar_r_max_dinamik_turetme]] §9.1 — "RC13'ün asıl darboğazı çoklu
> sefer değil, **%58'lik alt sınır boşluğudur** (zayıf LP gevşetmesi). Bu,
> `R_max` ile değil, kesme düzlemi / geçerli eşitsizlik / daha sıkı Big-M ile
> ele alınacak ayrı bir iştir." Bu sayfa o işi yapar ve o tahmini **doğrular**.

## 1. Sonuç önce — RC13'ün optimali bulundu ve KANITLANDI

| Model | Süre | Fizibil çözüm | Amaç | Alt sınır | Gap |
|---|---|---|---|---|---|
| `raw/` eşdeğeri (B0) | 900 s | **YOK** (`SolCount=0`) | — | 9720.2 | — |
| `raw/` (wiki kaydı, 1500 s / `NoRelHeurTime=500`) | 1500 s | var | 20753.8 | ~8680 | %58.2 |
| Güçlendirilmiş prototip (B9, `NoRelHeurTime=60`) | 68.3 s | var | **20667.0** | 20667.0 | %0.00 |
| **Güçlendirilmiş prototip (B9, `NoRelHeurTime=0`)** | **10.7 s** | var | **20667.0** | **20667.0** | **%0.00** |

(`NoRelHeurTime=60`'ın 58 s'lik farkı tamamen sezgisel ısınma süresidir —
güçlendirilmiş modelde bu bütçe **gereksizdir**, `raw/`'un `__main__` bloğundaki
`NoRelHeurTime=600` ayarı bu formülasyonda zararlıdır.)

**RC13 (EV) optimali = 20667.0.** Bu değer `raw/EV_v.1.1.py`'nin
**değiştirilmemiş** modelinde `x` değişkenleri sabitlenerek doğrulanmıştır
(`status=2`, `ObjVal = 20667.0`) — yani prototipin eklediği hiçbir kısıt
optimal çözümü kesmemiştir. Wiki'de "en iyi bilinen" olarak kayıtlı 20753.8
değeri optimalden **%0.42 kötüdür**; asıl kayıp çözüm kalitesinde değil,
**optimalliğin kanıtlanamamasındadır**.

## 2. Kök neden — LP gevşetmesinde DEPO ÇIKIŞI SIFIRDIR

RC13'ün (ve tüm diğer örneklerin) kök LP çözümü incelendiğinde:

```
RC13 EV, LP gevşetmesi:  obj = 7140.3
  toplam depo çıkışı  Σ_r Σ_j Σ_k x[O_r, j, k] = 0.000
  toplam aktif kaynak Σ_k z_veh[k]              = 0.000
  13 müşterinin tamamı 2-döngülerle kaplanmış:
      2↔5, 3↔11, 4↔8, 6↔10, 7↔12  (tam),  1–9–13 (kesirli 0.5'lik 3-döngü)
```

Yani LP, **hiç depoya uğramayan kapalı döngülerle** tüm müşterileri "ziyaret
edip" amaç fonksiyonunu her müşterinin en ucuz komşusuna indirmektedir. Neden
mümkün:

- **EV-2** (`raw/EV_v.1.1.py:247-251`) yalnızca "her müşterinin bir giren yayı
  olsun" der; yayın nereden geldiğini umursamaz.
- **EV-5** akış dengesi (`:304-311`) döngülerle sağlanır.
- **EV-4a/b/c** (`:265-277`) depo çıkışını `u[r,k] ≤ z_veh[k]`'ya bağlar; hiçbir
  kısıt `z_veh`'i **aşağıdan** zorlamaz, dolayısıyla `z=0, u=0` seçmek serbesttir.
- Alturları kesen tek mekanizma **EV-7'nin Big-M zaman zinciridir** (`:331-347`,
  `M = ls−es+(ll−el) = 39600`). Big-M kısıtları LP'de kesirli `x` altında
  **tamamen gevşektir**; altur elemesi ancak tamsayı düğümlerde devreye girer.

Bu, bir MTZ-tipi formülasyonun bilinen zayıflığıdır ve **RC13'e özgü değildir**
— aynı patoloji ölçülen **14 koşumun 14'ünde** (CV + EV × C5/R10/RC10/R13/RC13/
RC15/RC20) birebir görülmüştür (`depo_cikis_toplami = 0.000`, `z_toplami = 0.000`).

### 2.1 RC13'ü ÖZEL olarak zorlaştıran şey

Zayıflık genel, ama RC13'te birleşen üç etken gap'i patlatır:

1. **Zorunlu mola + zaman pencereleri = öğleden sonra sırt çantası problemi.**
   EV-12 (`:443-447`) her aktif kaynağa **tam bir** mola dayatır; EV-9 (`:396-404`)
   ve EV-11 (`:416-424`) ile birlikte ziyaret edilen her düğüm için şu **ayrık
   koşul** doğar: `τ_i + st_i ≤ el` **veya** `τ_i ≥ ll`. RC13'te 6 müşterinin
   `ec = 14400 = el` olduğundan (`raw/trsp_problem_sets/RC13 .xml`) bu 6 müşteri
   **zorunlu olarak** `τ ≥ ll = 21600`'e itilir. Öğleden sonra penceresi
   `ls − ll = 10800 s` ve bu 6 müşterinin toplam hizmet süresi **21903 s**'dir
   → en az `⌈21903/10800⌉ = 3` araç. Filoda tam 3 araç var
   (`raw/FC_Info4Vehicle4EV.xml`), yani RC13 **fizibilite sınırında** çalışıyor.
   Bu bir bin-packing alt problemidir ve mesafe amaçlı LP bunu hiç görmez.
2. **Kaynak sayısı `|K|` diğer 13'lüklerden büyük.** RC13'te 5 farklı
   `RequiredSkill` var → `|T| = 5 + C(5,2) = 15`, `|K| = 3·15 = 45`.
   C13'te yalnızca 4 beceri var → `|T| = 10`, `|K| = 30`. Bu, RC13'ün model
   boyutunu C13'e göre **%50 büyütür** (`NumVars` 19628 → 29423).
3. **Mesafe ölçeği.** RC13'te ortalama yay 1437 m (R13: 929 m), en uzun yay
   4387 m (R13: 2279 m). Optimal değer 20667 iken kök LP 7140'ta kalır.

## 3. Değerlendirilen hipotezler — hangileri DOĞRULANDI

| Hipotez | Karar | Kanıt |
|---|---|---|
| **Altur eleme yetersiz (EV-7 Big-M ile MTZ)** | **DOĞRULANDI — asıl neden** | LP çözümü tamamen 2-/3-döngülerden oluşuyor, depo çıkışı 0 (§2) |
| **Araç simetrisi** | **DOĞRULANDI (ikincil ama büyük)** | 3 araç birebir aynı (`BatteryCapacity=50000`, `MaxSpeed=37.5`, `Range=322000`); araç indisi tamamen kaldırıldığında `NumVars` 28703 → 9593, gap %58 → %28.6 |
| **Yetkinlik filtresinin `x` üzerinde uygulanmaması** | **DOĞRULANDI (saf boyut kaybı)** | `Ti_K[j]` yalnızca EV-2'de kullanılıyor (`:249`); `x[i,j,kk]` her `kk` için tanımlı. Yetkisiz `kk` sabitlemesi `NumVars` 28703 → 8615, **kök sınırı hiç değiştirmeden** |
| **Big-M gevşekliği** | **KISMEN — tek başına etkisiz** | Düğüm bazlı sıkı M (EV-6/7/30) LP sınırını RC13'te **hiç değiştirmedi** (13203.7 → 13203.7). Ancak `bwp` ile pencereler daraldığında dolaylı katkı sağlar |
| **İstasyon (şarj) mantığı ağır** | **DOĞRULANDI (formülasyonu zayıflatıyor)** | 4 istasyon düğümü yayların %40'ını üretiyor (`|At|` 182 → 306) ve DFJ kesitlerinin *göremediği* bir "kaçış yolu" açıyor: istasyonlar atıldığında LP 13203.7 → 14885.8 |
| **`R_max` (çoklu sefer)** | **ÇÜRÜTÜLDÜ (önceki tur)** | [[karar_r_max_dinamik_turetme]] §9.1; `R_max` zaten 1 |
| **Gurobi'nin kendi simetri tespiti yetersiz** | bkz. §5 | — |

## 4. Ölçümler — hangi müdahale ne kadar kazandırdı

Prototip anahtarları (hepsi `%TEMP%\rc13_diag\proto_ev.py`):

| Anahtar | Ne yapıyor | Geçerlilik dayanağı |
|---|---|---|
| `crew_fix` | `x[i,j,kk] = 0`, `j ∈ C` ve `kk ∉ Ti_K[j]` (ve simetrik olarak `i ∈ C`) | **Baskınlık**: yetkisiz kaynak `j`'den geçerse hem mesafe hem `st_j` bedeli öder, üçgen eşitsizliğiyle atlamak daha ucuzdur |
| `aggregate` | Homojen filoda araç indisini kaldırır: `K = T`, `Σ_t z[t] ≤ \|V\|` | Üç EV birebir aynı (`raw/FC_Info4Vehicle4EV.xml`); araç indisi **saf simetridir** |
| `bwp` | Mola penceresi yayılımı: `ec_i + st_i > el ⇒ ec_i := ll`; `lc_i < ll ⇒ lc_i := el − st_i` | EV-8/9/11/12 + EV-7 zincirinden türeyen ayrık koşul (§2.1-1) |
| `arc_fix` | `x[i,j,kk] = 0` eğer `tw_lb(i) + st_i + tt_ij > tw_ub(j)` | Zaman penceresi tutarsızlığı (molasız en gevşek hâl kullanılır → güvenli) |
| `dfj=n` | `\|S\| = 2..n` için `Σ_{i,j∈S} Σ_k x_{ijk} ≤ \|S\|−1`, `S ⊆ C` | DFJ/GSEC; `crew_fix` sonrası müşteri giriş/çıkış derecesi tam 1 olduğundan geçerli |
| `min_veh` | `Σ_r Σ_k u[r,k] ≥ ⌈öğleden sonra yükü / (ls−ll)⌉` | §2.1-1'deki sırt çantası argümanı |
| `drop_st` | Şarj istasyonu düğümlerini tamamen kaldırır | `max_single_trip_distance = 251 667 m < menzil 322 000 m` (`raw/xml_data_loader.py`, `derive_r_max`) → enerji hiç bağlamaz, istasyon **hiçbir zaman gerekmez** |
| `tight_m` | EV-6/7/30 Big-M'i `τ_ub(i) − τ_lb(j)` ile düğüm bazlı türetir | [[tight_big_m]] |

### 4.1 Kök sınır (RC13, LP ve kesmeli kök düğüm)

| Konfigürasyon | `NumVars` | LP | Kök (kesmeli) | Kök boşluğu* |
|---|---|---|---|---|
| B0 `raw/` eşdeğeri | 28 703 | 7140.3 | 7328.8 | **%64.5** |
| +`crew_fix` | 8 615 | 7140.3 | 7328.8 | %64.5 |
| +`aggregate` | 2 897 | 7166.3 | 7385.3 | %64.3 |
| +`bwp`+`arc_fix` | 2 837 | 7368.0 | 7391.7 | %64.2 |
| +`dfj=3` | 2 837 | 8099.7 | 8099.7 | %60.8 |
| **`min_veh` TEK BAŞINA (B0 üzerinde)** | 28 703 | **12 343.1** | **12 595.4** | **%39.1** |
| +`min_veh` (yığılmış) | 2 837 | 13 203.7 | 13 203.7 | %36.1 |
| +`tight_m` | 2 837 | 13 203.7 | 13 203.7 | %36.1 |
| +`drop_st` (B8) | 1 069 | 14 885.8 | 14 898.8 | %27.9 |
| **+`dfj=4` (B9)** | **1 069** | **15 195.5** | **15 491.1** | **%25.0** |

\* optimal 20667.0'a göre.

### 4.2 MIP performansı (RC13, EV, `TimeLimit=900 s`, `Seed=1`, `NoRelHeurTime=60`, `MIPGap=1e-4`)

| Konfigürasyon | `NumVars` | süre | çözüm | amaç | alt sınır | gap | düğüm | düğüm/s |
|---|---|---|---|---|---|---|---|---|
| B0 `raw/` eşdeğeri | 28 703 | 900 | **0** | — | 9720.2 | — | 48 748 | 54 |
| `min_veh` tek başına | 28 703 | 900 | 6 | 21 436.0 | 14 139.6 | %34.0 | 53 330 | 59 |
| B1 `crew_fix`+`aggregate` | 2 897 | 900 | 10 | **20 667.0** | 14 766.7 | %28.6 | 739 867 | 822 |
| B3 (+`bwp`+`arc_fix`) | 2 837 | 900 | 10 | **20 667.0** | 15 173.2 | %26.6 | 562 895 | 625 |
| B6 (+`bwp`+`arc_fix`+`dfj3`+`min_veh`) | 2 837 | 900 | 10 | **20 667.0** | 18 432.1 | %10.8 | 546 802 | 608 |
| **B9 tam** | **1 069** | **68.3** | 5 | **20 667.0** | 20 667.0 | **%0.00** | 6 692 | 98 |

### 4.3 Bileşen çıkarma (ablation) — GEÇERLİLİK ve HIZ katkısı

B9 tam konfigürasyonundan **tek bir bileşen** çıkarılarak koşuldu
(`TimeLimit=600 s`, `NoRelHeurTime=0`, `Seed=1`, `MIPGap=1e-4`):

| Çıkarılan | `NumVars` | süre | amaç | gap | düğüm |
|---|---|---|---|---|---|
| — (FULL) | 1 069 | **10.7 s** | 20 667.0 | %0.00 | 5 303 |
| `min_veh` | 1 069 | 14.5 s | **20 667.0** | %0.00 | 6 097 |
| `dfj` | 1 069 | **2.7 s** | **20 667.0** | %0.00 | 5 625 |
| `bwp`+`arc_fix` | 1 129 | 44.6 s | **20 667.0** | %0.00 | 37 929 |
| `drop_st` | 2 837 | **600 s (çözüm YOK)** | — | — | 320 892 |

İki kritik okuma:

1. **Geçerlilik ampirik olarak doğrulandı.** Dört ablasyonun **dördü de** aynı
   optimal değeri (`20667.0`) **kanıtladı**. Yani `min_veh`, `dfj`, `bwp`,
   `arc_fix` kısıtlarının hiçbiri optimal çözümü kesmiyor — §4'teki geçerlilik
   argümanları sayısal olarak destekleniyor.
2. **En büyük kaldıraç `drop_st`'tir.** İstasyonlar korunduğunda aynı model
   600 s'de **hiçbir fizibil çözüm bulamıyor** (10.7 s → >600 s). `bwp` ikinci
   sırada (10.7 s → 44.6 s, ~4×). Buna karşılık **statik DFJ kesitleri, diğer
   indirimler devredeyken NET ZARARLIDIR** (2.7 s → 10.7 s): kök sınırı
   yükseltiyor ama 1062 ek kısıtın düğüm başına maliyeti bunu geçiyor. DFJ'nin
   değeri, indirimler *olmadan* (B6: %58 → %10.8) ortaya çıkıyor.

İki bağımsız etki net biçimde ayrışıyor:

- **Boyut/simetri indirimi düğüm hızını 15× artırır** (54 → 822 düğüm/s). B1'de
  hiçbir yeni kesit yok, yalnızca `crew_fix` + `aggregate`; buna rağmen gap
  %58'den %28.6'ya iner ve optimal çözüm **bulunur** (kanıtlanamasa da).
- **Geçerli eşitsizlikler alt sınırı taşır.** `min_veh` **tek bir kısıttır** ve
  RC13'ü "900 s'de hiç çözüm yok"tan "%34 gap + %3.7 içinde bir çözüm"e taşır.

## 5. Gurobi parametreleri

(bkz. §7 — parametre taraması ayrı koşuldu; özet burada.)

Gurobi'nin kendi simetri tespiti (`Symmetry=2`, agresif) araç simetrisini
**modelleme düzeyinde kaldırmanın yerini tutmaz**: `aggregate` `NumVars`'ı
%66 düşürürken `Symmetry=2` model boyutuna dokunmaz. Presolve de yetkinlik
filtresini **bulamaz** (dominance-tabanlıdır, mantıksal değil): B0'da presolve
28 703 → 22 313 (%-22), `crew_fix` ise aynı işi %-70 ile yapar.

## 6. ÖNERİLER (öncelik sırasıyla)

Aşağıdakiler `raw/`'a **uygulanmamıştır**; her biri için gerekçe + ölçüm
yukarıdadır. Uygulama sırası, ölçülen kazanç/risk oranına göredir.

> **Asgari paket (ablasyonla doğrulanmış):** `Ö1 + Ö2 + Ö6` (yetkinlik
> filtresi + araç indisi kaldırma + enerji bağlamıyorsa istasyonları düşürme)
> RC13'ü **2.7 s'de kanıtlanmış optimale** getiriyor (`-dfj` satırı, §4.3).
> `Ö3`/`Ö4`/`Ö5` bu paketin üstünde **hız kazandırmıyor** (hatta DFJ zarar
> veriyor); değerleri, indirimlerin uygulanamadığı durumlarda (heterojen filo,
> gerçekten gereken istasyonlar, `n` büyüdükçe) ortaya çıkıyor.

### Ö1 (ZORUNLU, risk düşük) — Yetkinlik filtresini `x` üzerinde uygula
`build_model` içinde `x` değişken kümesini `(i,j,kk)` yerine
`{(i,j,kk) : kk ∈ Ti_K[j] ∩ Ti_K[i]}` ile kur. Kazanç: `NumVars` %-70,
düğüm hızı ~15×, **kök sınırda sıfır kayıp**. Not: bu, Faz 2'de `src/` altında
zaten yapılmış olan A5/`_crew_allowed` filtresinin `raw/`'a taşınmasıdır
([[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]).

### Ö2 (ZORUNLU, risk düşük) — Homojen filoda araç indisini kaldır
`K = V × T` yerine `K = T` + `Σ_t z[t] ≤ |V|`. Filo heterojenleşirse
(`Q`, `MaxSpeed`, `Range` farklılaşırsa) otomatik olarak eski hâle dönecek bir
kontrolle (`len(set(Q.values())) == 1`) korunmalı. Raporlama katmanı araç adı
beklediği için `print_ev_solution` uyarlanmalıdır — **tek gerçek entegrasyon
maliyeti budur**.

### Ö3 (EN YÜKSEK KAZANÇ/MALİYET, risk orta) — `min_veh` geçerli eşitsizliği
```python
# Σ_r Σ_k u[r,k] >= ceil(ogleden_sonra_yuku / (ls - ll))
```
**Kritik uyarı:** bu kesit `z` üzerine yazılırsa **etkisizdir** (EV-4c yalnızca
`u ≤ z` der; `z = 1` hiçbir depo yayını zorlamaz). Ölçüm: `z` üzerine yazılan
biçim LP'yi 7964.5 → 7964.5 (değişim yok), `u` üzerine yazılan biçim
7140.3 → 12 343.1 yaptı.

### Ö4 (risk orta) — Mola penceresi yayılımı (`bwp`)
`ec_i + st_i > el ⇒ ec_i := ll` ve `lc_i < ll ⇒ lc_i := el − st_i`.
**Yalnızca EV'de doğrudan geçerlidir** (EV-12 molayı zorunlu kılar). CV'de mola
opsiyoneldir (CV-13 `Σ w ≤ z`), dolayısıyla bu yayılım CV'ye **olduğu gibi
taşınamaz** — CV'de ancak `Σ w = z` koşullu bir ikili ile ifade edilebilir.

### Ö5 (risk orta) — DFJ altur kesitleri
`|S| = 2,3,4` için statik `Σ_{i,j∈S} Σ_k x ≤ |S|−1`. RC13'te 1062 kısıt, LP'yi
7368 → 15 196 taşıyor. Ölçek uyarısı: kısıt sayısı `O(n^4)`'tür; `n ≥ 40`'ta
statik ekleme yerine **lazy constraint callback** (tamsayı ayrıştırma) veya
kesirli ayrıştırma (min-cut) gerekir.

### Ö6 (risk düşük, kazanç yüksek) — Enerji bağlamıyorsa istasyonları düşür
`derive_r_max`'ın zaten hesapladığı `max_single_trip_distance ≤ menzil` testi
geçtiğinde (30/30 örnekte geçiyor, [[karar_r_max_dinamik_turetme]] §4.1)
`S = []` alınabilir. **Bu, `R_max = 1` türetiminin birebir aynı argümanıdır**
ve aynı kanıta dayanır. Kazanç: `|At|` 306 → 182, LP 13 203.7 → 14 885.8.
**Model genelliği açısından uyarı:** makale "EV + şarj istasyonu" iddiasında
bulunuyorsa, istasyonları düşürmek bir *veri-bağımlı ön işlemedir*, formülasyon
değişikliği değildir — sonuç raporunda böyle belirtilmelidir.

### Ö7 (risk düşük, kazanç küçük) — `tight_m` ve ölü kısıt temizliği
- EV-6/7/30 Big-M'lerini `τ_ub(i) − τ_lb(j)` ile düğüm bazlı türet
  ([[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] §7.1'in hâlâ
  uygulanmamış "bonus sıkılaştırma"sı). Tek başına LP'yi RC13'te değiştirmiyor,
  ama `bwp` ile birlikte anlamlı.
- `raw/EV_v.1.1.py:553` ve `:558` — `model.addConstr(ye[j] >= 0.0, ...)`
  **hiçbir şey yapmaz** (`ye` zaten `lb=0`) ve RC13'te **24 480 gereksiz kısıt**
  üretir (toplam 93 850'nin %26'sı). Presolve bunları atıyor, ama model kurma
  süresi ve `.lp` boyutu boşuna büyüyor.

## 7. Yan bulgular (ayrı sayfa gerektirebilir)

1. **Koşumlar tekrarlanabilir değil.** `raw/EV_v.1.1.py:953` ve
   `raw/CV_model_gurobi_exact.py`'deki `req_skills_unique = list(set(delivery_skills))`
   ifadesi, Python'un süreç bazında rastgeleleşen string hash'i nedeniyle
   **ekip (crew) adlarını ve `T` sıralamasını koşumdan koşuma değiştirir**
   (örn. aynı ikili bir koşumda `TECH_005_TECH_008`, diğerinde
   `TECH_008_TECH_005`). Bu, [[karar_r_max_dinamik_turetme]] §9.1'de
   "Gurobi'nin sezgisel şansı" olarak yorumlanan `R_max=3`/`R_max=1`
   ters dönmesinin **muhtemel gerçek nedenidir**. Düzeltme: `sorted(set(...))`.
2. **`Delta_s` fiilen ölü değişkendir.** `Delta_s[s,k]` yalnızca EV-6/EV-10/EV-15'te
   `≤` kısıtlarının **sol** tarafında pozitif katsayıyla geçer ve amaç
   fonksiyonunda yoktur → her optimal çözümde `0`'dır. Yani modelde **şarj süresi
   fiilen sıfırdır**. Bu, [[sorun_kismi_sarj_dinamikleri_kodda_yok]] ile birlikte
   değerlendirilmelidir.
3. **`ye`/`YE` düğüm-indekslidir, kaynak-indeksli değildir** (`raw/EV_v.1.1.py:170-171`).
   Müşteriler için sorun değil (EV-2 tek ziyaret garantiler) ama **bir şarj
   istasyonu iki farklı kaynak tarafından ziyaret edilirse aynı SoC değişkenini
   paylaşırlar** — model bunu engellemiyor (EV-3 yay bazlıdır, düğüm bazlı
   değil). Faz 2'de `src/` altında `(Np, K)` çok-indisli hâle getirilmişti
   ([[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]]); `raw/` bu düzeltmeyi
   miras almamış.
4. **CV modeli birebir aynı patolojiyi taşır** (`depo_cikis_toplami = 0.000`,
   7 örnekte). Ö1/Ö2/Ö3/Ö5/Ö7 CV'ye doğrudan taşınabilir; Ö4 (bwp) taşınamaz
   (CV'de mola opsiyonel), Ö6 CV'de zaten konusuz (CV'de istasyon düğümü yok,
   bkz. [[sorun_cv_kullanilmayan_istasyon_parametreleri]]).

## 8. Sınırlamalar / emin olunamayan noktalar

- `min_veh`'in geçerliliği **mola zorunluluğuna** (EV-12) ve `ec_i ≥ el` olan
  müşterilerin var olmasına dayanır. Formül tüm örneklerde `≥ 1` üretir (yani
  hiçbir zaman geçersiz olmaz), ama sıkılığı veri-bağımlıdır.
- DFJ kesitlerinin geçerliliği, müşteri giriş derecesinin **tam 1** olmasını
  gerektirir; bu ancak `crew_fix` uygulandıktan sonra kesindir. `crew_fix`'siz
  DFJ eklenmesi teorik olarak baskın-olmayan bir çözümü kesebilir (pratikte
  ölçülmedi).
- Prototip `print_ev_solution` / `raw/solution_validator.py` ile
  **doğrulanmamıştır**; doğrulama, çözümün `raw/` modelinde sabitlenip
  fizibil çıkması (§1) üzerinden dolaylı yapılmıştır.
- Ölçümler yalnızca **RC13 (EV)** üzerindedir; diğer örneklerde ve CV'de
  kazançlar tekrar ölçülmelidir.

## Sources

- `raw/EV_v.1.1.py:168-197` (değişken tanımları), `:247-277` (EV-2/3/4),
  `:304-311` (EV-5), `:331-347` (EV-7 Big-M), `:396-424` (EV-9/10/11),
  `:443-447` (EV-12), `:547-562` (EV-18/19, gereksiz `ye>=0`), `:583-597` (EV-24/25)
- `raw/CV_model_gurobi_exact.py:237-247` (CV-2/3), `:24-32` (`build_model` imzası)
- `raw/xml_data_loader.py:266-394` (`max_single_trip_distance`, `derive_r_max`)
- `raw/FC_Info4Vehicle4EV.xml` (3 birebir aynı araç), `raw/Info4Employee.xml`
  (5 beceri → 15 ekip), `raw/trsp_problem_sets/RC13 .xml`
- Prototip ve koşucular: `%TEMP%\rc13_diag\` (`proto_ev.py`, `lpcmp2.py`,
  `mipcmp.py`, `verify_raw.py`, `lp_general.py`) — `raw/` dışında

## Related

- [[sorun_rc20_darbogaz_kok_neden_analizi]] (**bu sayfanın DEVAMI, ama farklı bir teşhis**: RC20/n≥20 örneklerinde sorun LP zayıflığı değil, modelin **infeasible** olmasıdır — `{2,2,1}` beceri bölünmesi × 25 200 s günlük kapasite duvarı. Bu sayfadaki "§2 kök neden LP gevşetmesi" tespiti n ≤ 15 için geçerliliğini korur)
- [[karar_rc13_tam_paket_uygulamasi]] (bu sayfanın Ö3+Ö4+Ö7 önerilerini `raw/`'a uygulayan karar — RC13 EV 5.96s, RC15 EV 11.35s optimal)
- [[karar_rc13_asgari_paket_uygulamasi]] (bu sayfanın Ö1+Ö2+Ö6 önerilerini `raw/`'a uygulayan ve §1 iddiasını düzelten karar)
- [[karar_r_max_dinamik_turetme]] (§9.1 bu sayfanın çıkış noktası)
- [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] (§7.1 tight Big-M, §8.1 "LP zayıflar" öngörüsü)
- [[tight_big_m]]
- [[karar_a2_c1_birlesik_k_indeksi_ve_enerji_indeksleme]] (A5 yetkinlik filtresi, `src/`)
- [[uyumluluk_matrisi]]
- [[klon_dugum_node_replication]]
- [[celiski_ogle_molasi_zorunlulugu]]
- [[sorun_kismi_sarj_dinamikleri_kodda_yok]]
- [[gurobi_mip_cozucusu]]
