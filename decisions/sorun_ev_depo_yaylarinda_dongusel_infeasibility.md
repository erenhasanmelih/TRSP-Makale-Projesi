---
title: Sorun (Ölümcül, v1.1) — EV-17/18/19'un Depo Yaylarını Kapsaması Modeli Her Rota İçin Infeasible Yapıyordu
tags: [sorun, kritik, ev, enerji-kisiti, infeasibility, big-m, v1.1, cozuldu]
source: raw/EV_v.1.1.py
date: 2026-08-22
status: güncel
---

# Sorun (Ölümcül) — EV-17/18/19'un Depo Yaylarını Kapsaması

## Bulgu

v1.1'deki `raw/EV_v.1.1.py`, batarya kısıtlarını (EV-17, EV-18, EV-19) **tüm
`(i,j) ∈ A` çiftleri için**, yani depo yaylarını (`i = 0` ve `j = 0`) de dâhil ederek
yazıyordu. `ye_i` / `YE_i` değişkenleri (matematiksel modelde de) **yalnızca düğüm
indisli** olduğundan, `ye[0]` bütün kaynaklar ve bütün seferler için tek bir
değişkendir. Bu durumda seçilen bir `0 → c1 → … → cn → 0` kapalı turu boyunca EV-18
zinciri şuna indirgenir:

```
ye[c1] ≤ ye[0]  − h_e·d(0,c1)
ye[c2] ≤ ye[c1] − h_e·d(c1,c2)
...
ye[0]  ≤ ye[cn] − h_e·d(cn,0)
------------------------------------------------
ye[0]  ≤ ye[0]  − h_e·(tur toplam mesafesi)      ⇒  ÇELİŞKİ
```

Aynı yapı EV-17'de **zaman** boyutunda tekrarlanıyordu: EV-17 `i = 0` için
`tau[0,k] + tt(0,j) ≤ tau[j,k]` diyor, EV-7 ise `j = 0` için
`tau[i,k] + st_i + tt(i,0) ≤ tau[0,k]` diyor. `tau[0,k]` kodda **"depoya DÖNÜŞ
zamanı"** anlamına geldiğinden (bkz. `raw/CV_model_gurobi_exact.py`'deki "CV-26 geri
alındı" notu, satır 398-414) bu ikisi `tau[0,k] < tau[0,k]` döngüsel çelişkisini
üretiyordu — yani **CV-26/EV-21'in geri alınma gerekçesi EV-17 üzerinden arka kapıdan
geri sızmıştı.**

Sonuç: **EV modeli, herhangi bir müşteri ziyaret eden her çözüm için infeasible'dı.**

## Gurobi kanıtı (düzeltme öncesi)

C5 örneği, zaman penceresi/mesai kısıtları etkisiz hâle getirilerek (yapısal hatayı
izole etmek için) ve `0→1→5→4→0` turu `x = 1` ile sabitlenerek çözüldü:

```
status 3 (INFEASIBLE)
IIS boyutu: 8
Counter({'EV18': 4, 'FIX': 4})
   EV18_ub_0_1_EV_1_TECH_007_TECH_008
   EV18_ub_1_5_EV_1_TECH_007_TECH_008
   EV18_ub_5_4_EV_1_TECH_007_TECH_008
   EV18_ub_4_0_EV_1_TECH_007_TECH_008
   FIX_0_1  FIX_1_5  FIX_5_4  FIX_4_0
```

IIS **tam olarak** turu kapatan dört EV-18 kısıtından oluşuyor — yukarıdaki cebirsel
zincirin birebir sayısal doğrulaması. Ayrıca düzeltme öncesi C5 EV modeli 120 s'de
**hiç çözüm bulamıyordu** (`sols=0`).

Bu, "Değişiklik Raporu - v1.1.docx" §5.2'deki *"EV: 60 saniyelik kısa test süresinde
optimal bulunamadı (beklenen)"* ifadesinin gerçek nedenidir; bu bir performans sorunu
değil, yapısal infeasibility idi.

## Düzeltme

`raw/EV_v.1.1.py` içinde EV-17 (satır 326-358) ve EV-18/EV-19 (satır 376-399)
döngülerine, CV modelindeki muadillerinde (CV-19: `raw/CV_model_gurobi_exact.py:341-343`,
CV-20/21: `:352-355`) zaten var olan istisna eklendi:

```python
if i == 0 or j == 0:
    continue
```

Depo bacaklarının enerji tarafı, CV'deki CV-23/CV-24/CV-25 deseniyle birebir aynı
şekilde ayrı kısıtlara taşındı: bkz. [[karar_ev_depo_sarj_ve_donus_enerjisi_kisitlari]].

## Doğrulama (düzeltme sonrası)

- C5 EV: **feasible**, `obj = 8291.2` (CV modelinin C5 optimali ile aynı),
  `solution_validator.validate_solution` → `(True, [])`.
- Alt küme kısıtlarının hâlâ altur (subtour) elemeye yettiği kontrol edildi:
  müşteri-müşteri altturları EV-7 (i ∈ C), istasyon çıkışlı altturlar EV-6 (s ∈ S)
  tarafından zaten kesiliyor; depo yayları bu görevde kullanılmıyordu.

## ÇELİŞKİ (docx ↔ kod, çözülmedi)

`yeni dosyalarım/Matematiksel_Model_rev_v1.1/Matematiksel Model - CV ve EV.docx`
EV bölümünde **CV-23/CV-24/CV-25'in EV karşılığı yoktur**: CV modeli depo bacağı için
üç ayrı kısıt tanımlarken (docx paragraf 80-82), EV modeli (EV-17…EV-20, paragraf
151-154) yalnızca genel zincir kısıtlarını veriyor ve depoda tam şarj / dönüş enerjisi
kurallarını hiç tanımlamıyor. Yani **matematiksel modelin kendisi de eksik**; kod bu
eksiği EV-24/25/26/27 ile kapattı. Docx'in EV bölümünün buna göre güncellenmesi
gerekir. Bu başlık, docx güncellenene kadar açık kalır.

## Sources

- `raw/EV_v.1.1.py:314-358` (EV-17, düzeltilmiş)
- `raw/EV_v.1.1.py:360-399` (EV-18/EV-19, düzeltilmiş)
- `raw/CV_model_gurobi_exact.py:329-355` (CV-19/20/21 — depo istisnasının zaten var olduğu referans)
- `raw/CV_model_gurobi_exact.py:398-414` (CV-26 geri alınma notu — `tau[0,k]`'nin dönüş zamanı olduğu)
- `yeni dosyalarım/Matematiksel_Model_rev_v1.1/Matematiksel Model - CV ve EV.docx` (EV-17…EV-20; CV-23/24/25'in EV karşılığının yokluğu)

## Related

- [[karar_ev_depo_sarj_ve_donus_enerjisi_kisitlari]]
- [[sorun_ev17_big_m_gecersiz_kucuk]]
- [[sorun_v1_1_raw_faz2_duzeltmelerini_miras_almadi]]
- [[karar_a1_ev_sarj_c20_c21_duzeltmesi]]
- [[degisken_yakit_enerji_izleme]]
