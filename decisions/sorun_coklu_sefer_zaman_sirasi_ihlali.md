---
title: Sorun (ÇÖZÜLDÜ 2026-08-23) — CV-26/EV-21'in Geri Alınması "Zararsız" DEĞİLDİ; Çoklu Sefer Çizelgeleri Zaman Olarak Çakışıyordu
tags: [sorun, kritik, cv, ev, coklu-sefer, zaman-kisiti, klon-dugum, cozuldu]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py; raw/solution_validator.py
date: 2026-08-22
status: güncel
---

# Sorun — Çoklu Seferlerin Zaman Sırası Model Tarafından Garanti Edilmiyor

## Kodun iddiası

`raw/CV_model_gurobi_exact.py:411-427` (ve `raw/EV_v.1.1.py`'deki aynı not), CV-26'nın
(depodan ilk çıkış zaman ilerlemesi) geri alındığını, çünkü `τ_0k`'nin zaten "depoya
dönüş zamanı" olarak kullanıldığını ve bunun döngüsel infeasibility ürettiğini
söylüyor. Geri alınmanın **zararsız** olduğu, amaç fonksiyonunun `τ` sırasına değil
seçilen yaylara bağlı olduğu gerekçesiyle savunuluyor.

## Doğrulama sonucu: iddia KISMEN doğru, sonuç zararsız DEĞİL

- **Doğru olan kısım:** amaç fonksiyonu gerçekten `Σ d_ij·x_ijk`'dir
  (`raw/CV_model_gurobi_exact.py:127-130`), yani `τ` değerlerinden bağımsızdır.
  Ayrıca altur (subtour) eleme görevi CV-8/EV-7 tarafından üstlenildiği için depo
  yaylarının kısıttan çıkarılması alturlara kapı açmıyor.
- **Zararlı olan kısım:** `τ_0k` tek bir değişken olduğundan ve seferler arası
  sıralama kısıtı bulunmadığından, **aynı kaynağın (k) iki seferi zaman olarak
  çakışabiliyor.** Bu, rapor edilen çizelgeyi fiziksel olarak imkânsız yapar ve
  amaç değerini gerçekte olduğundan **iyimser** gösterir (gerçek bir çizelge daha
  fazla araç/mesafe gerektirirdi).

## Gurobi + solution_validator kanıtı

`raw/solution_validator.py`'nin `validate_solution()` fonksiyonu, CV modelinin
çoklu sefer üreten çözümlerinde **gerçek ihlal** buldu:

```
R10  h_c=0.055  status=9 obj=13138.2  valid=False  multitrip={('CV_3','TECH_003_TECH_001'): 2}
   ! SEFER SIRASI İHLALİ: kaynak ('CV_3','TECH_003_TECH_001') için
     sefer [0, 5, 4, 8, 0] [0.0-21600.0] ile sefer [0, 7, 0] [0.0-6589.2]
     zaman olarak çakışıyor (2. sefer, 1. sefer bitmeden başlıyor).

RC10 h_c=1.0    status=9 obj=12867.3  valid=False  multitrip={('CV_1','TECH_003_TECH_008'): 2}
   ! SEFER SIRASI İHLALİ: sefer [0, 7, 2, 9, 4, 0] [0.0-14163.4] ile
     sefer [0, 10, 3, 0] [0.0-10051.2] çakışıyor.
```

Her iki ihlalde de **her iki seferin türetilmiş çıkış saati 0.0** — yani model iki
seferi aynı anda başlatıyor. Tek sefer üreten çözümlerde (C5, C10, RC10/h_c=0.055)
doğrulayıcı `valid=True` veriyor; sorun **yalnızca çoklu sefer (CV-4/EV-4 ≥ 2)
kullanıldığında** ortaya çıkıyor.

Not: `raw/solution_validator.py`'nin kendi başlık yorumu (satır 15-19) bu riski zaten
teorik olarak öngörmüştü ("teorik olarak ihlal edilebilirler"); bu sayfa, riskin
**fiilen gerçekleştiğini** sayısal olarak belgeler.

## Neden düzeltilmedi

Doğru çözüm, kodun kendi notunda da yazdığı gibi, depo düğümünün her sefer için ayrı
bir zaman değişkenine sahip olması (klon düğüm / sefer-indeksli `τ`) veya en azından
sefer-indeksli bir sıralama değişkeni gerektirir. Mevcut `x_ijk` yapısında hangi depo
çıkışının hangi depo dönüşüyle eşleştiği **belirlenemediğinden**, güvenli (fizibıl
çözüm kesmeyen) bir sıralama kısıtı yazmak mümkün değil. Yarım bir kısıt eklemek
geçerli çözümleri kesme riski taşıdığı için bilinçli olarak yapılmadı; bu bir
**model seviyesinde** karar gerektiriyor (bkz. [[karar_klon_dugum_sarj_istasyonu_plani]]
ile aynı klonlama tekniği).

## Güncelleme (2026-08-22) — kalıcı çözüm TASARLANDI (henüz uygulanmadı)

Bu sayfanın "Neden düzeltilmedi" bölümünde işaret edilen model seviyesindeki
karar artık formal olarak tasarlandı ve `raw/` dışında bir prototip kopyada
Gurobi ile doğrulandı:
**[[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]]**.

Tasarımın özü: tek `tau[0,kk]` değişkeni, sefer indisli iki klon ailesiyle
(`o_r` = çıkış klonu, `e_r` = dönüş klonu) değiştirilir; sıralama kısıtı
`tau[e_r,kk] ≤ tau[o_{r+1},kk]` **iki farklı değişken** arasında yazıldığı
için CV-26/EV-21'in `tau[0,k] < tau[0,k]` döngüsüne düşmez.

Durum (2026-08-22 itibarıyla): **hâlâ AÇIK** — `raw/CV_model_gurobi_exact.py` ve
`raw/EV_v.1.1.py` değiştirilmedi; aşağıdaki ara önlem geçerliliğini koruyor.
**GÜNCELLEME: 2026-08-23'te çözüldü, bkz. aşağıdaki "ÇÖZÜLDÜ" bölümü.**

## Ara önlem (öneri — artık gereksiz, tarihsel kayıt)

Sonuçlar makaleye girmeden önce her çözüm için `validate_solution()` çalıştırılmalı;
`valid=False` çıkan örnekler ya raporlanmamalı ya da "çoklu sefer sıralaması model
tarafından garanti edilmiyor" dipnotuyla verilmelidir.

## ÇÖZÜLDÜ (2026-08-23)

[[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]] tasarımı `raw/` koduna
**uygulandı**. Depo düğümü sefer-indeksli çıkış/dönüş klonlarına ayrıldı ve
**CV-29/CV-30/CV-31** (`raw/CV_model_gurobi_exact.py:344-390`) ile **EV-28/EV-29/EV-30**
(`raw/EV_v.1.1.py:326-364`) eklendi. Sefer sırası artık `tau[E_r,k] ≤ tau[O_{r+1},k]`
biçiminde **iki farklı değişken** arasında yazıldığı için CV-26/EV-21'in
`tau[0,k] < tau[0,k]` döngüsüne düşmüyor.

### Kanıt 1 — ihlalin ortadan kalkması (R10, CV)

| Koşum | obj | `valid` | `multitrip` |
|---|---|---|---|
| Eski (klonsuz, belgelenen) | 13138.2 | **False** | `{('CV_3','TECH_003_TECH_001'): 2}` |
| Yeni (klonlu, `TimeLimit=900`) | **14335.3** | **True** | `{}` |

RC10 (CV, `TimeLimit=900`): `obj=10588.4`, `valid=True`.
C5/R5/RC5 regresyonu bozulmadı: sırasıyla `8291.2 / 10116.1 / 7933.0`, hepsi
`valid=True` ve `status=2` (optimal).

### Kanıt 2 — karşıt-olgusal (counterfactual) koşum

En güçlü kanıt: aynı yeni modelde `Σ_k u[2,k] ≥ 1` (çoklu seferi ZORLA) eklenerek
iki koşum yapıldı; ikincisinde **yalnızca `CV29_*` kısıtları kaldırıldı** (60 adet):

```
[R10 CV29-VAR] obj=15072.7  valid=True   multitrip={('CV_1','TECH_003_TECH_007'): 2}
      r=1: tau[o_1]=    0.0  tau[e_1]= 6589.2
      r=2: tau[o_2]= 6589.2  tau[e_2]=32400.0      <-- e_1 <= o_2, ZİNCİR DOĞRU

[R10 CV29-YOK] obj=13138.2  valid=False  multitrip={('CV_2','TECH_001_TECH_003'): 2}
   ! SEFER SIRASI İHLALİ: sefer [0,5,4,8,0] [0.0-17402.0] ile sefer [0,7,0]
     [0.0-6589.2] zaman olarak çakışıyor.
      r=1: tau[o_1]=0.0  tau[e_1]=32400.0
      r=2: tau[o_2]=0.0  tau[e_2]=32400.0          <-- İKİ SEFER DE 0.0'da
```

CV-29 kaldırıldığında bu sayfanın yukarıda belgelediği **birebir aynı ihlal**
(`obj=13138.2`, iki sefer de `0.0`'da, aynı `[0,5,4,8,0]` rotası) geri geliyor.
Yani ihlali kesen mekanizmanın tam olarak CV-29 olduğu izole edilmiş durumdadır.

### Yan etki (zorunlu)

Mola sayım tabanı "sefer sayısı"ndan "aktif kaynak"a çevrildi (CV-13 `≤ z[k]`,
EV-12 `== z_veh[k]`); aksi hâlde EV'de çoklu sefer *sessizce* imkânsız hâle
gelirdi. Bkz. [[celiski_ogle_molasi_zorunlulugu]] ve tasarım sayfası §6.

### `solution_validator.py`'nin yeni rolü

Kontrol 1 artık **yapısal olarak gereksizdir** (model garanti ediyor) ama
**regresyon testi olarak korunur** — yukarıdaki karşıt-olgusal koşum tam olarak
bu değeri gösteriyor.

## Sources

- `raw/CV_model_gurobi_exact.py:411-427` (CV-26 geri alınma notu ve "zararsız" iddiası)
- `raw/CV_model_gurobi_exact.py:127-130` (amaç fonksiyonu — iddianın doğru olan kısmı)
- `raw/EV_v.1.1.py:456-461` (EV-21 için aynı gerekçe)
- `raw/solution_validator.py:104-138` (Kontrol 1 ve Kontrol 2)

## Related

- [[celiski_single_trip_vs_multitrip]]
- [[karar_v1_1_coklu_sefer_ve_z_tekillik_kisitlari]]
- [[karar_klon_dugum_sarj_istasyonu_plani]]
- [[karar_klon_dugum_coklu_sefer_zaman_indeksleme_plani]]
- [[sorun_ev_depo_yaylarinda_dongusel_infeasibility]]
