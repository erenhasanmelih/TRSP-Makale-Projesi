---
title: Karar (UYGULANDI) — Depo Klon Düğümleriyle Sefer-İndeksli Zaman Değişkeni (CV-29/30/31, EV-28/29/30)
tags: [karar, uygulandi, klon-dugum, coklu-sefer, zaman-kisiti, big-m, cv, ev, mip-formulasyon]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py; raw/solution_validator.py
date: 2026-08-22
status: güncel
---

# Karar (UYGULANDI) — Depo Klon Düğümleriyle Sefer-İndeksli Zaman Değişkeni

> **Durum: UYGULANDI (2026-08-23).** Tasarım `raw/CV_model_gurobi_exact.py`
> ve `raw/EV_v.1.1.py`'ye doğrudan işlenmiştir; uygulama sonrası gerçek satır
> numaraları, Gurobi sonuçları ve sapmalar için bkz. **§13 Uygulama Sonucu**.
> §1-11 tasarımı, §12 uygulama öncesi prototip doğrulamasını belgeler.
>
> (Tarihsel not: bu sayfa 2026-08-22'de "PLANLANDI, UYGULANMADI" durumuyla
> yazılmıştı; doğrulama o gün `raw/` dışında bir prototip kopyada yapılmıştı.)
>
> Bu sayfa, **depo** düğümünün sefer bazlı klonlanmasıyla ilgilidir.
> **Şarj istasyonu** düğümlerinin klonlanması ayrı bir konudur:
> [[karar_klon_dugum_sarj_istasyonu_plani]]. İkisi aynı tekniğin
> ([[klon_dugum_node_replication]]) farklı düğüm ailelerine uygulanmasıdır
> ve ortak bir klon altyapısıyla birlikte gerçekleştirilmelidir (bkz. §8).

## 1. Çözülen sorun

[[sorun_coklu_sefer_zaman_sirasi_ihlali]] sayfasında sayısal olarak
belgelenen hata: CV-4/EV-4 bir kaynağın (`kk = (v,t)`) günde ≤3 sefer
yapmasına izin veriyor
(`raw/CV_model_gurobi_exact.py:149-153`, `raw/EV_v.1.1.py:170-174`), ama
depo düğümünün zaman değişkeni `tau[0,kk]` **kaynak başına tek bir
skalerdir** (`raw/CV_model_gurobi_exact.py:90`, `raw/EV_v.1.1.py:101`).
CV-8/EV-7'nin `j = 0` hâli bu tek değişkeni "depoya dönüş zamanı" olarak
sabitler (`raw/CV_model_gurobi_exact.py:225-240`), dolayısıyla aynı
değişken "çıkış zamanı" olarak kullanılamaz. Bu yüzden aynı kaynağın 2. ve
3. seferleri **zaman olarak çakışabiliyor** (R10'da her iki sefer de
`τ = 0.0`'da başlıyor).

Kök neden, `x[i,j,kk]` yay değişkenlerinin *sefer sırasını* taşımamasıdır:
hangi depo çıkışının hangi depo dönüşüyle eşleştiği belirlenemez.

## 2. Tasarımın özü — iki klon ailesi

Tek bir `0` düğümü, **her sefer için ayrı bir çıkış klonu ve ayrı bir dönüş
klonu** ile değiştirilir:

```
R      = {1, ..., R_max}          # sefer indisi, R_max = 3 (CV-4/EV-4 ile aynı)
O      = { o_r : r ∈ R }          # depo ÇIKIŞ klonları — yalnızca ÇIKAN yay
E      = { e_r : r ∈ R }          # depo DÖNÜŞ klonları — yalnızca GİREN yay
Cs     = C ∪ S                    # müşteri + (EV'de) şarj istasyonu düğümleri
Ñ      = Cs ∪ O ∪ E               # genişletilmiş düğüm kümesi (fiziksel 0 ARTIK YOK)
```

Yay kümesi:

```
Ã = { (i,j) : i,j ∈ Cs, (i,j) ∈ A }          # iç yaylar — DEĞİŞMEZ
  ∪ { (o_r, j) : r ∈ R, j ∈ Cs, (0,j) ∈ A }  # depo çıkışları, sefer-indeksli
  ∪ { (i, e_r) : r ∈ R, i ∈ Cs, (i,0) ∈ A }  # depo dönüşleri, sefer-indeksli
```

Kasıtlı olarak **yok**: `O`'ya giren yay, `E`'den çıkan yay, `o_r → e_r`
yayı. Bunun iki sonucu var: (a) hiçbir altur bir depo klonunu içeremez —
formülasyon *sıkılaşır*; (b) "boş sefer" bir yayla değil, `u[r,kk] = 0`
ile temsil edilir.

Parametreler klonlara **fiziksel depodan takma ad (alias)** yoluyla taşınır
(`build_model` içinde yerel kopya; çağıranın `data` sözlüğü değiştirilmez):

```python
d[o_r, j]  = d[0, j];   tt[o_r, j] = tt[0, j]
d[i, e_r]  = d[i, 0];   tt[i, e_r] = tt[i, 0]
st[o_r] = st[e_r] = 0.0
ec[o_r] = ec[e_r] = ec[0];  lc[o_r] = lc[e_r] = lc[0]
```

`kk_name` / `K` / `z` yapısı **hiç değişmez**: klonlama düğüm ekseninde
olur, kaynak ekseninde değil. Bu, [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]
ile kurulan `z[v,t]` (CV-27/EV-22) ve teknisyen tekilliği (CV-28/EV-23)
kısıtlarını olduğu gibi korur.

## 3. Karar değişkenleri

| Değişken | Eski | Yeni | Not |
|---|---|---|---|
| `x[i,j,kk]` | `(i,j) ∈ A` | `(i,j) ∈ Ã` | anlamı aynı; depo yayları artık sefer-indeksli |
| `tau[i,kk]` | `i ∈ N0` | `i ∈ Ñ` | `tau[o_r,kk]` = **r. seferin çıkışı**, `tau[e_r,kk]` = **r. seferin dönüşü** |
| `w[i,j,kk]` | `(i,j) ∈ A` | `(i,j) ∈ Ã` | değişmez |
| `u[r,kk]` | — | **YENİ**, binary | "kaynak `kk`, `r`. seferi yapıyor" |
| `z[kk]` / `z_veh[kk]` | binary | değişmez | araç-ekip ataması |
| `yc/YC` (CV), `ye/YE` (EV) | `N0` üzerinde | `Ñ` üzerinde | düğüm-indeksli kalır; klon girdileri yalnızca yer tutucudur |
| `Delta_c[s,kk]` / `Delta_s[s,kk]` | değişmez | değişmez | istasyonlar klonlanmaz (bkz. §8) |

Kritik nokta: `tau[o_r,kk]` ve `tau[e_r,kk]` **farklı değişkenlerdir**.
Geri alınan CV-26/EV-21'in döngüsel çelişkisi tam olarak bu ikisinin aynı
değişken olmasından kaynaklanıyordu.

## 4. Kısıt formülasyonları (gurobipy)

Aşağıda yalnızca **değişen veya yeni eklenen** kısıtlar verilmiştir; adı
geçmeyen tüm kısıtlar (CV-2, CV-3, CV-6, CV-7, CV-9, CV-10, CV-11, CV-12,
CV-17, CV-18, CV-27, CV-28 ve EV muadilleri) döngü alanı `N0 → Ñ`,
`A → Ã` olarak genişletildiğinde **biçimsel olarak aynı kalır**.

### 4.1 CV-4 / EV-4 → dört parçalı klonlu çoklu sefer

```python
for kk in K:
    for r in R:
        m.addConstr(gp.quicksum(x[O[r], j, kk] for j in Cs if (O[r], j) in At) == u[r, kk],
                    name=f"CV4a_cikis_{r}_{kk_name[kk]}")
        m.addConstr(gp.quicksum(x[i, E[r], kk] for i in Cs if (i, E[r]) in At) == u[r, kk],
                    name=f"CV4b_donus_{r}_{kk_name[kk]}")
        m.addConstr(u[r, kk] <= z[kk], name=f"CV4c_z_bagi_{r}_{kk_name[kk]}")
    for r in R[:-1]:                       # simetri kırma
        m.addConstr(u[r + 1, kk] <= u[r, kk], name=f"CV4d_sira_{r}_{kk_name[kk]}")
```

Toplandığında eski CV-4 geri gelir: `Σ_r Σ_j x[o_r,j,kk] = Σ_r u[r,kk] ≤ 3·z[kk]`.
`CV4d` yeni bir simetri kırma kazancıdır (kullanılmayan sefer indisleri
her zaman sondadır).

### 4.2 CV-5 / EV-5 — akış dengesi artık YALNIZCA ara düğümlerde

```python
for i in Cs:                               # dikkat: N0 değil, Cs (klonlar hariç)
    for kk in K:
        m.addConstr(gp.quicksum(x[i, j, kk] for j in Ñ if (i, j) in At)
                    - gp.quicksum(x[j, i, kk] for j in Ñ if (j, i) in At) == 0, ...)
```

Depo tarafındaki akış dengesi artık CV-4a/4b tarafından, hem de **daha
sıkı** biçimde sağlanır: eski `for i in N0` döngüsü yalnızca "toplam çıkış
= toplam dönüş" diyordu; yenisi her `r` için ayrı ayrı `çıkış_r = dönüş_r = u_r`
diyor.

### 4.3 CV-29 / EV-28 (YENİ) — SEFER SIRASI

```python
for kk in K:
    _, t_ = kk
    for r in R[:-1]:
        m.addConstr(
            tau[E[r], kk] <= tau[O[r + 1], kk] + (ls[t_] - es[t_]) * (1 - u[r + 1, kk]),
            name=f"CV29_sefer_sirasi_{r}_{kk_name[kk]}"
        )
```

Bu, sorunun doğrudan çözümüdür: `r`. seferin dönüşü, `r+1`. seferin
çıkışından sonra olamaz.

### 4.4 CV-30 / EV-29 (YENİ) — kullanılmayan sefer klonlarının ankrajı

```python
for kk in K:
    _, t_ = kk
    for r in R:
        m.addConstr(tau[O[r], kk] <= es[t_] + (ls[t_] - es[t_]) * u[r, kk],
                    name=f"CV30o_bos_sefer_{r}_{kk_name[kk]}")
        m.addConstr(tau[E[r], kk] <= es[t_] + (ls[t_] - es[t_]) * u[r, kk],
                    name=f"CV30e_bos_sefer_{r}_{kk_name[kk]}")
```

`u[r,kk] = 0` iken (CV-15'in `tau ≥ es` alt sınırıyla birlikte) klon zaman
değişkenleri `es`'e sabitlenir. Bu bir **dejenerasyon/simetri temizliğidir**:
serbest yüzen `tau` değişkenleri Branch-and-Bound'da eşdeğer düğüm kopyaları
üretir. CV-29'daki `u`-koruması bununla birlikte zorunludur (aksi hâlde
kullanılan bir `r` seferinin dönüşü, kullanılmayan `r+1`'in `es`'e sabitlenmiş
çıkışından önce olmak zorunda kalırdı).

### 4.5 CV-31 / EV-30 (YENİ) — depodan çıkış zaman ilerlemesi (geri alınan CV-26'nın DOĞRU hâli)

```python
for r in R:
    for j in Cs:
        if (O[r], j) not in At:
            continue
        for kk in K:
            _, t_ = kk
            bigM = max(0.0, ls[t_] - es[t_] - tt[O[r], j])
            m.addConstr(
                tau[O[r], kk]
                + w[O[r], j, kk] * (ll[t_] - el[t_])
                + tt[O[r], j] * x[O[r], j, kk]
                - bigM * (1 - x[O[r], j, kk])
                <= tau[j, kk],
                name=f"CV31_depo_cikis_zaman_{r}_{j}_{kk_name[kk]}"
            )
```

### 4.6 Depo yayına atıf yapan kısıtların yeniden yazımı

| Kısıt | Eski (raw) | Yeni |
|---|---|---|
| CV-13 (mola üst sınırı) | `Σ w ≤ Σ_j x[0,j,kk]` (`:283-288`) | `Σ w ≤ z[kk]` — bkz. §6 uyarısı |
| EV-12 (zorunlu mola) | `Σ w == Σ_j x[0,j,kk]` (`:283-288`) | `Σ w == z[kk]` — bkz. §6 uyarısı (**zorunlu değişiklik**) |
| CV-14 (molasız erken dönüş) | `x[i,0,kk]` (`:299-303`) | `Σ_r x[i,e_r,kk]` |
| CV-15/16, EV-13/14 | `tt[0,i]`, `tt[i,0]` | klonlar için 0; diğer düğümler değişmez |
| CV-19 / EV-17 | `if i == 0 or j == 0: continue` (`:342`, `:331`) | `if i in O∪E or j in O∪E: continue` |
| CV-20/21, EV-18/19 | aynı filtre | aynı biçimde klon filtresi |
| CV-22 | `for i in N0 if i != 0` (`:372-377`) | `for i in Cs` |
| CV-23/24, EV-24/25 | `x[0,j,kk]` (`:383-397`, `:416-428`) | her `r` için `x[o_r,j,kk]`, mesafe `d[0,j]` |
| CV-25 / EV-26 | `x[i,0,kk]` (`:400-409`, `:437-444`) | `Σ_r x[i,e_r,kk]` (toplulaştırılmış — en fazla bir terim 1'dir) |

CV-19/EV-17'nin depo yayı istisnası **korunur**; bu, bu oturumda düzeltilen
[[sorun_ev_depo_yaylarinda_dongusel_infeasibility]] hatasının geri gelmemesi
için kritiktir.

## 5. Neden bu tasarım döngüye girmiyor

Geri alınan CV-26 şu çelişkiyi üretiyordu
(`raw/CV_model_gurobi_exact.py:411-427`):

```
CV-8 (j=0):   tau[0,k] ≥ tau[son müşteri,k] + st + tt   → tau[0,k] "dönüş"
CV-26   :     tau[0,k] + tt[0, ilk müşteri] ≤ tau[ilk müşteri,k]  → tau[0,k] "çıkış"
⇒ tau[0,k] + (pozitif tur süresi) ≤ tau[0,k]     ⇒ INFEASIBLE
```

Klonlu tasarımda zaman değişkenleri üzerindeki **öncelik grafiği bir
DAG**'dır. Seçilen yaylar üzerinde tanımlı kenarlar (`u → v` = "`tau_u + δ ≤ tau_v`,
`δ > 0`"):

```
o_1 → (trip 1 zinciri) → e_1 → o_2 → (trip 2 zinciri) → e_2 → o_3 → ... → e_3
 ↑CV-31          ↑CV-8/CV-6      ↑CV-29
```

- `O` düğümlerinin **giren kenarı yok** (yalnızca CV-29 ile `e_{r-1}`'den).
- `E` düğümlerinin **çıkan kenarı yok** (yalnızca CV-29 ile `o_{r+1}`'e).
- Her müşteri CV-2 gereği tam olarak bir kez ziyaret edildiğinden, seçilen
  yaylar üzerinde her müşterinin en fazla bir giren + bir çıkan kenarı vardır.

Sonuç: seçilen alt-graf **doğrusal bir zincirdir**, dolayısıyla çevrim
içeremez. Seçilmeyen yaylar Big-M ile devre dışı kalır.

### 5.1 Sefer eşleşmesinin "çaprazlanması" neden imkânsız?

CV-4a/4b, `o_1`'den çıkan zincirin `e_1`'de bitmesini **kombinatoryal olarak**
zorlamaz; zincir `e_2`'de de bitebilir. Ancak bu, zaman kısıtlarıyla
otomatik olarak elenir. Çapraz durumda (`o_1 → … → e_2` ve `o_2 → … → e_1`):

```
CV-31 + CV-8:   tau[o_2] + (pozitif süre) ≤ tau[e_1]
CV-29      :    tau[e_1] ≤ tau[o_2]
⇒ çelişki
```

Bu bir **kayıp değildir**: her fiziksel çoklu sefer çizelgesi, seferler
kronolojik sıraya göre `r = 1,2,3` etiketlenerek çaprazsız temsil
edilebilir. Yani kısıt, genelliği kaybettirmeden geçerli çözüm uzayını
tam olarak korur (`w.l.o.g.`). Bedeli: çaprazlama LP gevşetmesinde hâlâ
mümkündür, yani bu eleme dal-sınır ağacında Big-M üzerinden gerçekleşir.
Sefer-üyeliği değişkeni (`y[i,j,kk,r]`) ile bunu LP düzeyinde de kesmek
mümkündür ama bu, [[karar_4b_to_3b_index_reduction_plani]] ile kazanılan
indis düşürmeyi geri alır — **bilinçli olarak tercih edilmedi**.

## 6. Yan etki uyarısı — mola sayısı kısıtı ZORUNLU olarak değişmeli

Bu tasarımın uygulanması, mola kısıtlarında bir düzeltmeyi **zorunlu**
kılar. Mevcut hâl:

- CV-13: `Σ w[i,j,kk] ≤ Σ_j x[0,j,kk]` (= sefer sayısı) — `raw/CV_model_gurobi_exact.py:283-288`
- EV-12: `Σ w[i,j,kk] == Σ_j x[0,j,kk]` (= sefer sayısı) — `raw/EV_v.1.1.py:283-288`

Yani model, 2 sefer yapan bir kaynağa 2 mola *veriyor* (EV'de zorunlu
kılıyor). Ama mola penceresi günde tek ve sabittir (`el=14400`, `ll=21600`;
`raw/xml_data_loader.py:226-227`). CV-10 mola öncesi hizmetin `el`'den önce
bitmesini, CV-12 mola sonrası düğüme `ll`'den sonra varılmasını dayattığı
için **iki mola aynı `[el, ll]` penceresini işgal etmek zorundadır**.
Sefer sırası kısıtı (CV-29) yokken bu tutarsızlık gizli kalıyordu; CV-29
eklendiğinde:

```
1. sefer molası ⇒ tau[e_1] ≥ ll
2. sefer molası ⇒ tau[o_2] ≤ el
CV-29          ⇒ tau[e_1] ≤ tau[o_2]
⇒ ll ≤ el   ⇒ ÇELİŞKİ
```

**Sonuç:** EV-12 eşitlik olarak bırakılırsa, klon tasarımı EV modelinde
çoklu seferi *sessizce* imkânsız hâle getirir (model infeasible olmaz;
Gurobi yalnızca `u[2,kk] = 0` seçer ve EV fiilen tek-seferli modele geri
döner). Bu, düzeltmenin **ölçülemez** hâle gelmesi demektir.

**Önerilen düzeltme (fiziksel olarak da doğrusu):** günde kaynak başına
en fazla / tam olarak **bir** öğle molası:

```python
# CV-13'
m.addConstr(gp.quicksum(w[i, j, kk] for (i, j) in At) <= z[kk], name=f"CV13_mola_max_{kk_name[kk]}")
# EV-12'
model.addConstr(gp.quicksum(w[i, j, kk] for (i, j) in At) == z_veh[kk], name=f"EV12_mola_zorunlu_{kk_name[kk]}")
```

Bu, [[celiski_ogle_molasi_zorunlulugu]] ile birlikte değerlendirilmelidir
(CV opsiyonel / EV zorunlu ayrımı bu değişiklikle korunur, yalnızca sayım
tabanı "sefer sayısı"ndan "aktif kaynak"a çevrilir). Prototipte CV-13'
biçimi kullanılmıştır.

## 7. Big-M türetimleri (tight)

[[tight_big_m]] ve [[karar_c2_tight_big_m_uygulamasi]] yaklaşımına uygun
olarak yeni kısıtların hiçbiri sabit bir `100000.0` kullanmaz; hepsi
vardiya penceresi genişliğinden türetilir.

| Kısıt | M | Türetim |
|---|---|---|
| **CV-29 / EV-28** | `ls[t] - es[t]` | `u_{r+1}=0` iken gevşemesi için: `max τ[e_r] − min τ[o_{r+1}] = ls − es`. **Tam (exact) sınır.** |
| **CV-30 / EV-29** | `ls[t] - es[t]` | `u=1` iken üst sınır `ls`'ye, `u=0` iken `es`'e iner. Tam sınır. |
| **CV-31 / EV-30** | `max(0, ls[t] - es[t] - tt[o_r, j])` | `x=0` ⇒ CV-9 gereği `w=0`; gereken: `τ[o_r] − M ≤ τ[j]`. `τ[o_r] ≤ ls` (CV-16, klonda `st=0, tt=0`) ve `τ[j] ≥ es + tt[0,j]` (CV-15) ⇒ `M ≥ ls − es − tt[0,j]`. **Yay-bazlı tam sınır.** |

### 7.1 Bonus sıkılaştırma fırsatı (mevcut CV-8/EV-7)

Aynı türetim mevcut CV-8'e uygulandığında, kodda kullanılan
`bigM = ls[t_] + (ll[t_] - el[t_])` (`raw/CV_model_gurobi_exact.py:232`)
**gereğinden gevşektir**: `x[i,j,kk] = 0` iken CV-9 gereği `w[i,j,kk] = 0`
olduğundan `(ll − el)` terimi kısıta hiç girmez ve `es` alt sınırı da
düşürülebilir. Sıkı hâli:

```python
bigM = max(0.0, ls[t_] - es[t_] - tt[i, j])       # CV-8 / EV-7 için
```

Mevcut veriyle (`es = 0`) fark `(ll − el) + tt[i,j] = 7200 + tt` kadardır.
Bu, bu tasarımdan bağımsız uygulanabilir ayrı bir iyileştirmedir; prototipte
`ls − es + (ll − el)` biçimi (yani yalnızca `es` düzeltmesi) kullanılmıştır.

## 8. Karmaşıklık ve ölçek etkisi (dürüst değerlendirme)

`n = |C| (+|S|)`, `R_max = 3`, `|K| = |V|·|T|`.

| Büyüklük | Eski | Yeni | Oran |
|---|---|---|---|
| Düğüm | `n + 1` | `n + 2·R_max` = `n + 6` | `+5` |
| Yay | `n² + n` | `n² − n + 2·R_max·n` = `n² + 5n` | `n=10 → 1.36×`, `n=50 → 1.08×`, `n=100 → 1.04×` |
| İkili değişken (`x`, `w`) | `2·|A|·|K|` | `2·|Ã|·|K|` | yukarıdaki oranla aynı |
| İkili değişken (`u`) | — | `R_max·|K|` | ihmal edilebilir |
| Sürekli `tau` | `(n+1)·|K|` | `(n+6)·|K|` | `+5·|K|` |
| Yeni kısıt CV-31 | — | `R_max·n·|K|` | CV-8'in `n(n+1)|K|`'sına göre `≈ 3/(n+1)` |
| CV-23/24 | `n·|K|` | `R_max·n·|K|` | `3×` (ama küçük bir grup) |

**Kritik gözlem:** klonlanan yaylar yalnızca depo yaylarıdır ve bunlar
toplam yayların `O(n)/O(n²)` kadarını oluşturur. Bu nedenle **büyüme oranı
`n` arttıkça 1'e yakınsar** — yani R100/C100 gibi büyük setlerde model boyutu
neredeyse hiç artmaz (%4 civarı). Ölçek maliyeti asıl olarak küçük setlerde
(n≈10) hissedilir.

**Dürüst risk değerlendirmesi:**

1. **LP gevşetmesi zayıflar.** Sefer eşleşmesi (§5.1) yalnızca Big-M zaman
   kısıtlarıyla elendiğinden, kök LP daha gevşek olabilir ve dal-sınır ağacı
   büyüyebilir. Prototipte R10, 900 s'de `%28.7` gap ile bitti (taban model
   aynı setle `status=9`, yani zaten zaman limitine takılıyordu — ama daha
   düşük, *geçersiz* bir objektif değeriyle).
2. **Objektif değeri KÖTÜLEŞİR — ve bu doğrudur.** Klon modeli R10'da
   `obj = 14335.3` verdi; taban model `obj = 13138.2` veriyordu ama o çözüm
   `valid=False` idi ([[sorun_coklu_sefer_zaman_sirasi_ihlali]]). Yani
   ~%9'luk artış, kaldırılan **iyimserlik yanlılığının** ölçüsüdür, bir
   gerileme değil.
3. **Mitigasyon — `R_max` parametreleştirilmeli.** `R_max` sabit 3 yerine
   `build_model` argümanı yapılmalı ve büyük setlerde veriden türetilmeli
   (örn. `2·(min gidiş-dönüş süresi + min hizmet süresi) > ls − es` ise
   `R_max = 1`). Bu, R100/C100 gibi setlerde klonlama maliyetini tamamen
   sıfırlar.

   > ### Uygulandı (2026-08-24)
   >
   > `R_max` artık `raw/xml_data_loader.py`'deki `derive_r_max()` tarafından
   > veriden türetiliyor ve `data['R_max']` ile her iki modele taşınıyor.
   > Ayrıntılı gerekçe, kanıt ve ölçümler: **[[karar_r_max_dinamik_turetme]]**.
   >
   > **Önemli düzeltme — yukarıdaki formül YANLIŞTI.** `2·(min gidiş-dönüş +
   > min hizmet)` mevcut veride ≈ 2×1400 = 2800 s'dir, `ls − es` ise
   > 32400 s; yani koşul **hiçbir örnekte** sağlanmaz ve bu formül `R_max`'ı
   > hiç düşürmez (ölçülen: `⌊(ls−es)/f_min⌋ = 18…30`, 27 örnek).
   >
   > **İşe yarayan argüman farklıdır — birleştirme baskınlığı (merge
   > dominance):** ardışık iki sefer `… → i → depo → j → …` tek sefere
   > birleştirilirse üçgen eşitsizliği gereği amaç kötüleşmez ve zaman/mola
   > kısıtları korunur (mevcut `τ` değerleri aynen geçerlidir); **tek engel
   > enerjidir**, çünkü depoda yeniden dolum yalnızca çıkış yayında verilir
   > (CV-23/24, EV-24/25). Dolayısıyla *bir vardiyaya sığabilen en uzun
   > rotanın uzunluğu menzilden küçükse* `R_max = 1` optimal değeri korur.
   >
   > Ölçüm: CV'de `maxdist ∈ [11.8, 81.5] km < 109.1 km` menzil; EV'de
   > `maxdist ≤ 79.6 km < 322 km` (EV'de belirleyici terim **zorunlu
   > moladır**: bütçe 32400−7200 = 25200 s). **27/27 örnekte `R_max = 1`.**
   >
   > Sonuç: klon maliyeti yalnızca "sıfırlanmadı", model taban modelden
   > **küçüldü** — CV `NumVars` %-39.6, EV %-26.8 (C5/R5/RC5). C5/R5/RC5 ×
   > {CV, EV} altı koşumda objektif **birebir aynı** kaldı (`valid=True`),
   > yani türetim optimal çözümü kesmiyor.
4. **Kazanç tarafı:** CV-4d simetri kırma + CV-30 dejenerasyon ankrajı +
   depo klonlarının altur içerememesi, formülasyonu bazı yönlerden
   *sıkılaştırır*. Net etki ampiriktir; uygulama sonrası R10/RC10/C10 +
   bir büyük set üzerinde A/B koşumu yapılmalıdır.

## 9. CV ↔ EV simetrisi

Tasarım iki modele **birebir simetrik** uygulanır; tek fark isimlendirme
ve enerji değişkenleridir:

| | CV (`raw/CV_model_gurobi_exact.py`) | EV (`raw/EV_v.1.1.py`) |
|---|---|---|
| Düğüm kümesi | `N0` → `Ñ` | `N_prime` → `Ñ` |
| Enerji | `yc/YC`, `G[v]`, `h_c` | `ye/YE`, `Q[v]`, `h_e` |
| İstasyon | `Fc` (fiilen boş, `real_stations`) | `S` (gerçek istasyonlar) |
| Atama değişkeni | `z[kk]` | `z_veh[kk]` |
| Yeni kısıt no. | CV-29 / CV-30 / CV-31 | EV-28 / EV-29 / EV-30 |
| Mola kısıtı | CV-13 `≤ z[kk]` | EV-12 `== z_veh[kk]` (§6) |

**EV şarj mantığıyla çakışma denetimi (bu oturumda düzeltilen A1/EV-24-27):**

- **EV-24/EV-25 (depoda tam şarj, `raw/EV_v.1.1.py:416-428`)**: `x[0,j,kk]`
  yerine `x[o_r,j,kk]` yazılır; mesafe `d[0,j]` aynı kalır (klon takma adı).
  Her `j` için `R_max` kat fazla kısıt oluşur ama en fazla biri aktiftir
  (`x` en fazla bir `r` için 1) → davranış birebir korunur. Bu, çoklu
  seferin kullandığı tek şarj mekanizması olduğundan (kod notu, `:413-415`)
  klonlama bu mekanizmayı **güçlendirir**: artık her seferin başındaki tam
  şarj ayrı bir yay üzerinden ifade edilir.
- **EV-26 (dönüş enerjisi, `:437-444`)**: `x[i,0,kk]` → `Σ_r x[i,e_r,kk]`.
  İstasyon düğümleri de kapsandığı için `YE[i]` kullanımı korunur.
- **EV-18'in istasyon istisnası (A1 düzeltmesi, `:380-394`)**: istasyonlar
  `Cs` içinde kaldığından `i not in S_set` filtresi hiç etkilenmez.
- **EV-27 (`YE[i] == ye[i]`, `i ∈ C`, `:453-454`)**: alanı yalnızca `C`
  olduğundan klonlardan etkilenmez.
- **EV-17 depo yayı istisnası (`:331-332`)**: `i == 0 or j == 0` filtresi
  `i in O∪E or j in O∪E` olarak genişletilmelidir — **atlanırsa
  [[sorun_ev_depo_yaylarinda_dongusel_infeasibility]] geri gelir** (klonlar
  arası zincirle değil, ama `ye[o_r]`/`ye[e_r]` yer tutucuları üzerinden
  sahte kısıt üretir).

Çakışma bulunmadı: EV'nin şarj mantığı **düğüm-içi** (istasyonda `Delta_s`,
`YE − ye`), klonlama ise **düğüm-arası** (depo yayı ayrıştırması) çalışır.

## 10. Raporlama ve doğrulayıcı üzerindeki yan kazançlar

- `print_cv_solution` / `print_ev_solution`, depodan çıkış saatini şu an
  "ilk müşteriden geriye doğru türeterek" hesaplıyor
  (`raw/CV_model_gurobi_exact.py:550-557`, `raw/EV_v.1.1.py:582-583`) —
  çünkü `tau[0,kk]` çıkış zamanı değil. Klonlarla çıkış saati **doğrudan**
  `tau[o_r,kk].X`, dönüş saati `tau[e_r,kk].X` olarak okunabilir; türetme
  hack'i kaldırılabilir.
- Sefer ayrıştırması (`next_map` / `depot_departures`,
  `raw/CV_model_gurobi_exact.py:508-531`) `i == 0` yerine `i in O` ile
  yapılır ve `r` indisi zaten kronolojik sırayı verir — `depot_departures.sort()`
  (düğüm numarasına göre keyfi sıralama) gereksizleşir.
- `raw/solution_validator.py`'nin Kontrol 1'i (`:104-116`) **yapısal olarak
  gereksizleşir** ama regresyon testi olarak korunmalıdır.

## 11. Reddedilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| MTZ tarzı sefer sayacı `p[i,kk]` (düğüm başına "kaçıncı sefer") | Ek bir Big-M katmanı gerektirir ve sefer başına ayrı çıkış/dönüş zamanı vermez; asıl sorunu (tek `tau[0,kk]`) çözmez. |
| Tek klon ailesi (`0_r`, hem giren hem çıkan yay) | Klon başına iki `tau` değişkeni gerektirir; `for i in N0` biçimindeki tüm jenerik kısıtların hangi `tau`'yu kullanacağı belirsizleşir. İki aile (`O`/`E`) tek bir `tau` dizisiyle çalışır. |
| Sefer-üyeliği değişkeni `y[i,j,kk,r]` (LP'de çaprazlama kesme) | 3B indise dönüşü ([[karar_4b_to_3b_index_reduction_plani]]) geri alır, değişken sayısını `R_max` kat artırır. |
| Çoklu seferi tamamen kaldırmak (`R_max = 1`) | [[celiski_single_trip_vs_multitrip]]'te kapatılan docx↔kod çelişkisini yeniden açar. |

## 12. Prototip doğrulaması

`raw/` **değiştirilmeden**, tasarımın birebir kopyası geçici bir dosyada
(`%TEMP%\trsp_klon_prototip.py`) uygulanıp Gurobi 13 ile çözüldü ve
`raw/solution_validator.validate_solution()` ile denetlendi (klon
düğümleri `0`'a geri eşleyen bir kabuk üzerinden).

Prototipin (`%TEMP%\trsp_klon_prototip.py`, `build_model_clone`) R10 üzerindeki
sonucu: `obj = 14335.3`, `valid = True`, 900 s'de `%28.7` gap. Taban (klonsuz)
model aynı setle `obj = 13138.2` veriyordu ama o çözüm `valid = False` idi.
Prototipin bir zayıflığı, doğrulayıcı kabuğunun (`_Shim`) klon yaylarını `0`'a
eşlerken **sözlük çakışması** yaşaması ve aynı `(0,j,kk)` anahtarına düşen
farklı `r` değişkenlerinden yalnızca sonuncusunu tutmasıydı; §13'teki uygulama
doğrulamasında bu, çakışan değişkenlerin **maksimumunu** taşıyan bir vekil
(`_Proxy`) ile kayıpsız hâle getirilmiştir.

## 13. Uygulama Sonucu (2026-08-23)

### 13.1 `raw/` içinde ne değişti (gerçek satır aralıkları)

**`raw/CV_model_gurobi_exact.py`**

| Bölüm | Satır | Not |
|---|---|---|
| `build_model(..., R_max=3)` imzası | `24-31` | `R_max` artık **parametre** (§8.3 mitigasyonu) |
| Klon kümeleri `R`, `Cs`, `O`, `E`, `clones`, `Nt`, `At`, parametre takma adları | `88-152` | fiziksel `0` düğümü yay kümesinden çıkarıldı |
| Değişkenler `x`, `tau`, `YC`, `yc`, `w` artık `Nt`/`At` üzerinde | `154-160` | |
| **YENİ** `u[r,kk]` | `177-179` | ikili |
| `m._O/_E/_R/_u/_z/_Nt/_clones` bağlama | `188-203` | raporlama + dış doğrulayıcı için |
| **CV-4a/b/c/d** (eski tek CV-4'ün yerine) | `223-243` | |
| CV-5 akış dengesi artık yalnızca `Cs` | `278-289` | |
| CV-8 `j ∈ Nt` (E klonları dahil), Big-M `ls−es+(ll−el)` | `320-338` | §7.1'in `es` düzeltmesi |
| **CV-31** (YENİ, depodan çıkış zaman ilerlemesi) | `339-361` | tight `max(0, ls−es−tt[o_r,j])` |
| **CV-29** (YENİ, sefer sırası) | `363-374` | tight `ls−es` |
| **CV-30** (YENİ, boş sefer ankrajı) | `376-391` | tight `ls−es` |
| **CV-13** mola: `≤ Σ_j x[0,j,k]` → **`≤ z[kk]`** | `431-450` | §6 zorunlu değişikliği |
| CV-14 `x[i,0,k]` → `Σ_r x[i,E_r,k]` | `452-468` | |
| CV-15/16 klonlarda `tt=0` | `470-481` | |
| CV-19, CV-20/21 klon yayı filtresi (`i in clones or j in clones`) | `498-540` | eski `i==0 or j==0`'ın karşılığı |
| CV-22 `for i in Cs` | `541-547` | |
| CV-23/24 her `r` için ayrı | `549-570` | mesafe `d[0,j]` (takma ad) |
| CV-25 `Σ_r x[i,E_r,k]` ile toplulaştırıldı | `572-583` | |
| "CV-26 geri alındı" notu → "CV-26 TARİHÇESİ, ÇÖZÜLDÜ" | `585-599` | |
| `print_cv_solution` klon farkındalığı (`i in O`, `r` = kronolojik sıra, `_break_on` yardımcısı) | `672-724`, `775-786` | |

**`raw/EV_v.1.1.py`** (birebir simetrik)

| Bölüm | Satır |
|---|---|
| Klon kümeleri + parametre takma adları (`tt_0i`/`tt_i0` dahil) | `98-156` |
| Değişkenler `Nt`/`At` üzerinde | `158-164` |
| **YENİ** `u[r,kk]` | `186-188` |
| `model._O/_E/_R/_u/_z/_Nt/_clones` | `201-215` |
| **EV-4a/b/c/d** | `237-254` |
| EV-5 yalnızca `Cs` | `278-288` |
| EV-7 `j ∈ Nt` | `308-324` |
| **EV-30** (YENİ) | `326-343` |
| **EV-28** (YENİ, sefer sırası) | `345-352` |
| **EV-29** (YENİ, ankraj) | `354-366` |
| **EV-12** mola: `== Σ_j x[0,j,k]` → **`== z_veh[kk]`** | `403-424` |
| EV-13/14 klonlarda `tt_0i=tt_i0=0` | `426-435` |
| EV-16 `for i in Nt` (klon `ec`/`lc` takma adı) | `446-450` |
| EV-17, EV-18/19 klon filtresi | `452-539` |
| EV-20 `for i in Nt` | `541-545` |
| EV-24/25 her `r` için | `547-574` |
| EV-26 `Σ_r x[i,E_r,k]` | `576-593` |
| "EV-21 geri alındı" notu → "ÇÖZÜLDÜ" | `602-609` |
| `print_ev_solution` klon farkındalığı | `690-742`, `769-775` |

`R_max`, CV'de `build_model(..., R_max=3)` argümanı, EV'de `data["R_max"]`
(varsayılan 3) olarak parametreleştirildi.

### 13.2 Gurobi doğrulaması — hepsi `valid=True`

Doğrulama, `raw/solution_validator.validate_solution()` ile, klon düğümlerini
`0`'a **kayıpsız** eşleyen (`_Proxy` = çakışan değişkenlerin maksimumu) bir
kabuk üzerinden yapıldı. Koşucular `raw/` DIŞINDADIR
(`%TEMP%\trsp_klon_test\run_cv.py`, `run_ev.py`).

| Örnek | Model | `TimeLimit` | `status` | `obj` | `gap` | `valid` |
|---|---|---|---|---|---|---|
| C5 | CV | 180 s | 2 (optimal) | 8291.2 | %0.0 | **True** |
| R5 | CV | 300 s | 2 (optimal) | 10116.1 | %0.0 | **True** |
| RC5 | CV | 300 s | 2 (optimal) | 7933.0 | %0.0 | **True** |
| **R10** | CV | 900 s | 9 | **14335.3** | %32.4 | **True** |
| **RC10** | CV | 900 s | 9 | **10588.4** | %33.4 | **True** |
| C5 | EV | 180 s | 9 | 8291.2 | %32.1 | **True** |
| R5 | EV | 300 s | 2 (optimal) | 10116.1 | %0.0 | **True** |
| RC5 | EV | 300 s | 2 (optimal) | 7933.0 | %0.0 | **True** |
| **R10** | EV | 300 s | 9 | 14633.8 | %45.7 | **True** |
| **RC10** | EV | 300 s | 9 | 13285.1 | %58.9 | **True** |
| RC13 (istasyonlu, `\|C\|=13`) | EV | 1500 s | 9 | 20898.0 | %58.5 | **True** |

C5/R5/RC5 satırları **regresyon kontrolüdür**: bu üç örnek klonlama öncesinde de
doğru çalışıyordu ve bozulmadıkları görülüyor (CV'de üçü de `status=2`, optimal).

### 13.2.1 RC13 uyarısı — `R_max=3` FİZİBİL ÇÖZÜM BULMAYI zorlaştırıyor

RC13 (EV) ilk denemede **`TimeLimit=600 s`, `NoRelHeurTime=60 s`** ile
`solcount=0` verdi. Bunun bir modelleme hatası değil, §8.1'de öngörülen
**"LP gevşetmesi zayıflar, dal-sınır ağacı büyür"** riskinin gerçekleşmesi
olduğu üç koşumla izole edildi:

| Koşum | `R_max` | `TimeLimit` | `NoRelHeurTime` | Sonuç |
|---|---|---|---|---|
| A | 3 | 600 s | 60 s | `solcount=0` (fizibil çözüm yok) |
| B | **1** | 600 s | 300 s | `obj=20667.0`, **valid=True** |
| C | 3 | 1500 s | 500 s | `obj=20898.0`, **valid=True** |

B, A ile **aynı klon makinesini** kullanır (yalnızca `R_max` farklı), yani sorun
klonlamanın kendisinde değil, `R_max=3`'ün getirdiği arama uzayı genişlemesinde
ve yetersiz sezgisel bütçededir. C, `R_max=3` ile de çözüm bulunabildiğini
gösteriyor.

**Pratik sonuç:** §8.3'teki `R_max` mitigasyonu bir "iyi olurdu" değil,
**operasyonel bir gerekliliktir**. Büyük setlerde ya `R_max` veriden
türetilmeli ya da `NoRelHeurTime` yükseltilmelidir. `raw/EV_v.1.1.py`'nin
`__main__` bloğu zaten `TimeLimit=10800`, `NoRelHeurTime=600` kullandığından
üretim koşumları bu tuzağa düşmez.

> ### ÇELİŞKİ — bu çıkarım yeniden üretilemedi (2026-08-25)
>
> `R_max` veriden türetildikten sonra ([[karar_r_max_dinamik_turetme]])
> RC13 A/B koşumu tekrarlandığında **yukarıdaki A/B gözlemi tersine döndü**:
>
> | `TimeLimit` / `NoRelHeurTime` | `R_max=3` | `R_max=1` |
> |---|---|---|
> | 600 s / 60 s (2026-08-23, satır A/B) | `solcount=0` | `obj=20667.0` |
> | 600 s / 60 s (2026-08-25, tekrar) | `obj=21214.3` | **`solcount=0`** |
> | 1500 s / 500 s (2026-08-25) | `obj=20753.8` | `obj=20753.8` (birebir aynı) |
>
> Yani RC13'te fizibil çözüm bulma başarısı `R_max`'a değil Gurobi'nin
> sezgisel şansına bağlıdır ve tek koşuma dayanan yukarıdaki "operasyonel
> gereklilik" çıkarımı **desteklenmemektedir**. Bu başlık, geçmiş korunsun
> diye silinmemiştir. Ayrıntı: [[karar_r_max_dinamik_turetme]] §9.1.
>
> (`R_max`'ın veriden türetilmesi yine de uygulandı — gerekçesi hız değil,
> **model boyutu ve formülasyon doğruluğu**dur.)

### 13.3 Objektif değişimi — §8.2 tahmini DOĞRULANDI

R10 (CV) için §8.2'nin öngörüsü **birebir tuttu**:
`13138.2 (valid=False) → 14335.3 (valid=True)`, yani **+%9.1**. Bu artış bir
gerileme değil, kaldırılan **iyimserlik yanlılığının** ölçüsüdür.

RC10 (CV) için ise objektif **düştü**: `12867.3 → 10588.4`. Bu bir çelişki
değil, iki nedenin bileşimi: (a) belgelenen `12867.3` değeri `h_c = 1.0` ile
alınmıştı, oysa A7 düzeltmesinden sonra `h_c` XML'den (`0.055`) okunuyor
(bkz. [[karar_a7_cv_yakit_tuketim_orani_duzeltmesi]]); (b) her iki koşum da
zaman limitine takılı **incumbent** değerlerdir, optimal değil. Yani
RC10 satırı bir "iyileşme" olarak değil, **karşılaştırılamaz** olarak
raporlanmalıdır.

### 13.4 KARŞIT-OLGUSAL (counterfactual) kanıt — asıl doğrulama

Zaman limitine takılan koşumlarda `multitrip = {}` çıktığı için (Gurobi
incumbent'ları çoklu sefer kullanmadı), düzeltmenin gerçekten çalıştığını
göstermek üzere çoklu sefer **zorlandı** (`Σ_k u[2,k] ≥ 1`) ve iki koşum
karşılaştırıldı:

**CV, R10, 240 s:**

```
CV29-VAR  obj=15072.7  valid=True   multitrip={('CV_1','TECH_003_TECH_007'):2}
          r=1: tau[o_1]=   0.0  tau[e_1]= 6589.2
          r=2: tau[o_2]=6589.2  tau[e_2]=32400.0        <-- e_1 <= o_2 ZİNCİRİ

CV29-YOK  obj=13138.2  valid=False  multitrip={('CV_2','TECH_001_TECH_003'):2}
   ! SEFER SIRASI İHLALİ: [0,5,4,8,0] [0.0-17402.0] ile [0,7,0] [0.0-6589.2]
          r=1: tau[o_1]=0.0  tau[e_1]=32400.0
          r=2: tau[o_2]=0.0  tau[e_2]=32400.0           <-- İKİ SEFER DE 0.0
```

Yalnızca 60 adet `CV29_*` kısıtı kaldırıldığında
[[sorun_coklu_sefer_zaman_sirasi_ihlali]]'nde belgelenen **birebir aynı**
ihlal (`obj=13138.2`, aynı rota, ikisi de `0.0`) geri geliyor. İhlali kesen
mekanizma böylece CV-29 olarak **izole edilmiştir**.

**EV, R10, 240 s (§6'nın mola değişikliğinin testi):**

```
EV12-YENI (== z_veh)   obj=15072.8  valid=True
          multitrip={('EV_3','TECH_007_TECH_003'):2}   mola sayısı=1
          r=1: tau[o_1]=   0.0  tau[e_1]= 6603.2
          r=2: tau[o_2]=6603.2  tau[e_2]=32400.0

EV12-ESKI (== sefer sayısı)   solcount=0  (240 s VE 900 s'de hiçbir fizibil çözüm yok)
```

(Not: Gurobi her iki koşumda da `status=9` (TimeLimit) ile bitti, yani
infeasibility **ispatlanmadı**; ancak 900 s'de tek bir fizibil çözüm bile
bulunamaması, §6'daki `ll ≤ el` çelişkisi türetimiyle tutarlıdır.)

§6'nın öngörüsü doğrulandı ve **daha da keskin çıktı**: çoklu sefer *zorlandığında*
eski EV-12 biçimi modeli fizibil çözümsüz bırakıyor (`ll ≤ el` çelişkisi).
Zorlanmadığında ise (§6'nın dediği gibi) infeasible olmaz, Gurobi sessizce
`u[2,k]=0` seçerdi — yani düzeltme ölçülemez hâle gelirdi. Bu, mola sayım
tabanının "sefer sayısı"ndan "aktif kaynak"a çevrilmesinin **zorunlu** olduğunu
kanıtlar.

### 13.5 Model boyutu — §8 tablosu DOĞRULANDI

`R_max=1` (klonlamanın maliyetsiz sınır hâli, taban modelin yakın vekili) ile
`R_max=3` arasında ölçülen büyüme:

| Örnek | `|C|` | `|K|` | değişken oranı | kısıt oranı | nz oranı | §8 tahmini `(n²+5n)/(n²+n)` |
|---|---|---|---|---|---|---|
| R10 | 10 | 30 | **1.366×** | 1.187× | 1.276× | 1.364× |
| R20 | 20 | 45 | **1.192×** | 1.090× | 1.152× | 1.190× |

Ölçülen değişken oranı, §8'in analitik tahminiyle **üçüncü haneye kadar**
örtüşüyor. Büyüme oranı `n` arttıkça 1'e yakınsıyor (§8'in "büyük setlerde
%4-8" öngörüsü `n≈50-100` içindir; `n=20`'de henüz %19).

### 13.6 Raporlama fonksiyonları

`print_cv_solution` / `print_ev_solution` klon farkındalığı kazandı: depo
çıkışları `i == 0` yerine `i ∈ O` ile bulunuyor, `r` indisi **kronolojik
sıralamayı doğrudan veriyor** (§10) ve her sefer başlığında
`(model: τ[o_r] = ..., τ[e_r] = ...)` teşhis satırı yazılıyor. Görüntülenen
çizelge, fiziksel olarak en sıkı hâli koruması için hâlâ türetilmiş değeri
(`τ[ilk müşteri] − tt[0,ilk müşteri]`) kullanıyor — `τ[o_r]` serbestçe daha
erken olabildiği için (araç depoda bekliyor demektir). §10'un "türetme hack'i
kaldırılabilir" önerisi bu nedenle **kısmen** uygulandı: hack kaldırılmadı,
yanına model değeri eklendi.

Mola göstergesi (`w`) depo yaylarında klon-indeksli olduğundan, raporda
`w[prev, 0, kk]` doğrudan okunamaz; `_break_on(pos)` yardımcısı `0`'ları
`O[r_out]`/`E[r_in]`'e geri eşler.

### 13.7 Ertelenen / yapılmayanlar

- **Şarj istasyonu klonlaması** hâlâ uygulanmadı
  ([[karar_klon_dugum_sarj_istasyonu_plani]]). Depo uygulaması ona yeniden
  kullanılabilir bir kalıp (klon kimliği, parametre takma adı, `clones`
  filtresi) bıraktı.
- **§7.1'in CV-8/EV-7 bonus sıkılaştırması** yalnızca `es` düzeltmesi
  düzeyinde uygulandı (`ls−es+(ll−el)`); `max(0, ls−es−tt[i,j])` biçimine
  geçilmedi (mevcut veride `es=0` olduğu için sayısal fark yalnızca
  `(ll−el)+tt[i,j]`; ayrı bir iyileştirme olarak bırakıldı).
- ~~**`R_max`'ın veriden türetilmesi** (§8.3) yapılmadı; yalnızca
  parametreleştirildi.~~ **YAPILDI (2026-08-24)** →
  [[karar_r_max_dinamik_turetme]]. §8.3'ün önerdiği formülün geçersiz
  olduğu, işe yarayan argümanın "birleştirme baskınlığı + enerji testi"
  olduğu ortaya çıktı; 27/27 örnekte `R_max = 1`.
- **`R_max=3` ile fizibil çözüm bulma zorluğu** (§13.2.1) giderilmedi; yalnızca
  ölçüldü ve nedeni izole edildi.
- Test edilen EV örneklerinde **hiçbir şarj istasyonu ziyaret edilmedi**
  (`ziyaret edilen istasyonlar=[]`) — batarya (50 kWh / 322 km) bu ölçekteki
  mesafeler için fazlasıyla yeterli. Yani klonlamanın EV şarj mantığıyla
  çakışmadığı (§9) *yapısal olarak* doğrulandı, ancak **aktif bir istasyon
  ziyareti üzerinde ampirik olarak sınanamadı**.

## Sources

- `raw/CV_model_gurobi_exact.py:88-97` (mevcut değişken tanımları), `:144-153` (CV-4),
  `:187-194` (CV-5), `:225-240` (CV-8), `:280-303` (CV-13/14), `:341-351` (CV-19),
  `:379-409` (CV-23/24/25), `:411-427` (CV-26 geri alınma notu)
- `raw/EV_v.1.1.py:99-125` (değişkenler), `:167-174` (EV-4), `:198-206` (EV-5),
  `:281-288` (EV-12), `:315-358` (EV-17), `:407-454` (EV-24/25/26/27),
  `:456-460` (EV-21 geri alınma notu)
- `raw/solution_validator.py:104-138` (Kontrol 1/2)
- `raw/xml_data_loader.py:219-298` (CV veri hazırlığı, `el`/`ll` varsayılanları)
- [[sorun_coklu_sefer_zaman_sirasi_ihlali]] (sorunun sayısal kanıtı)

## Related

- [[sorun_rc13_darbogaz_kok_neden_analizi]] (§7.1 tight Big-M ve §13.2.1 "R_max mitigasyonu" öngörüleri RC13'te yeniden değerlendirildi)
- [[sorun_coklu_sefer_zaman_sirasi_ihlali]]
- [[karar_klon_dugum_sarj_istasyonu_plani]]
- [[klon_dugum_node_replication]]
- [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]
- [[celiski_single_trip_vs_multitrip]]
- [[celiski_ogle_molasi_zorunlulugu]]
- [[tight_big_m]]
- [[karar_c2_tight_big_m_uygulamasi]]
- [[karar_4b_to_3b_index_reduction_plani]]
- [[sorun_ev_depo_yaylarinda_dongusel_infeasibility]]
- [[solution_validator_fonksiyonlari]]
