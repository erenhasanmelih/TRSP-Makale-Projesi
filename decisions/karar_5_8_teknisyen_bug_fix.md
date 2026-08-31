---
title: Karar (UYGULANDI) — 5/8 Teknisyen Bug Fix (skill_tech_map[skill][0] → Tüm Teknisyenler)
tags: [karar, uygulandi, bug-fix, teknisyen, ekip-atama, raw, ev, cv]
source: raw/CV_model_gurobi_exact.py; raw/EV_v.1.1.py; raw/Info4Employee.xml
date: 2026-08-31
status: güncel
---

# Karar (UYGULANDI) — 5/8 Teknisyen Bug Fix

> **Durum: UYGULANDI (2026-08-31), Eren'in açık talimatıyla.**
> [[sorun_rc20_darbogaz_kok_neden_analizi]] §2-1'de teşhis edilen hata
> doğrudan `raw/CV_model_gurobi_exact.py:1087` ve `raw/EV_v.1.1.py:1188`'de
> düzeltildi.

## 1. Hata neydi

`raw/Info4Employee.xml`'de 5 beceri (`s1..s5`) ve toplam **8 teknisyen**
tanımlı (`s1→[TECH_001,TECH_002]`, `s2→[TECH_003,TECH_004]`,
`s3→[TECH_005,TECH_006]`, `s4→[TECH_007]`, `s5→[TECH_008]`). Kod her
beceriden yalnızca **ilk** teknisyeni aktifleştiriyordu:

```python
tech = skill_tech_map[skill][0]   # eski hâl
```

Sonuç: `TECH_002/004/006` hiçbir koşumda hiç kullanılmadı — model 8 değil,
fiilen 5 teknisyenle çalışıyordu. Bu, [[sorun_rc20_darbogaz_kok_neden_analizi]]
tarafından RC20'nin (ve n≥20 tüm örneklerin) INFEASIBLE olmasının kök
nedenlerinden biri olarak izole edildi (o sayfanın "Ö-A: tam kadro" seçeneği
— bu karar birebir onu uygular).

## 2. Düzeltme

```python
for skill in req_skills_unique:
    if skill in skill_tech_map and skill_tech_map[skill]:
        for tech in skill_tech_map[skill]:   # [0] yerine TÜM teknisyenler
            active_techs.append(tech)
            tech_to_skill[tech] = skill
```

`raw/CV_model_gurobi_exact.py` (aynı blok, `:1085-1090` civarı) ve
`raw/EV_v.1.1.py` (`:1186-1190` civarı) birebir aynı şekilde düzeltildi.

## 3. Neden bu bir "bug fix", bir "veri/senaryo kararı" değil

[[sorun_rc20_darbogaz_kok_neden_analizi]] §5 bu değişikliği ("Ö-A: tam
kadro") diğer üç seçenekle (Ö-B filo 3→4, Ö-C vardiya penceresi genişletme,
Ö-D n≥20'yi kapsam dışı bırakma) birlikte "problem tanımını değiştiren,
onay gerektiren" kararlar olarak sıralamıştı. Bu ayrı değerlendirilmelidir:
Ö-B/Ö-C/Ö-D gerçekten veri/senaryo kararlarıdır (kaç araç var, vardiya kaç
saat — bunlar TRSP probleminin *girdisidir*). Ö-A ise farklıdır: `raw/`'un
kendi girdi dosyası (`Info4Employee.xml`) zaten 8 teknisyen tanımlıyor, kod
bunlardan 3'ünü **sessizce görmezden geliyordu** — bu veri ile kod
arasındaki bir tutarsızlıktır, yeni bir senaryo varsayımı değildir.
Dolayısıyla Eren bu düzeltmeyi (yalnızca bunu) uygulamaya onay verdi;
Ö-B/Ö-C/Ö-D hâlâ UYGULANMADI ve RC20 üzerinde başka hiçbir işlem
yapılmadı.

## 4. Doğrulama — ÖNEMLİ: RC13/RC15'in bilinen optimalleri de İYİLEŞTİ

`raw/` dışı bir regresyon testiyle (`%TEMP%\...\scratchpad\regression_test.py`
— `raw/`'un `__main__`'ı interaktif `input()` içerdiğinden, ilgili modül
`runpy` ile fonksiyon düzeyinde import edilip `__main__` bloğunun mantığı
kısa bir `TimeLimit` ile tekrarlandı):

| Örnek | Model | Önce (5/8 teknisyen, bug'lı) | Sonra (8/8 teknisyen, düzeltilmiş) |
|---|---|---|---|
| C5 | CV | 8291.18 (optimal, ~0 s) | **8291.18 (optimal, birebir aynı)** — ekip ataması artık `TECH_002/003/007/008` içeriyor |
| RC13 | EV | 20666.99 (optimal, 5.96 s) | **19938.07 (optimal, 12.87 s)** — **%3,5 DAHA İYİ**, gap %0.00 |
| RC15 | EV | 23912.82 (optimal, 11.35 s) | **21851.58 (optimal, 32.15 s)** — **%8,6 DAHA İYİ**, gap %0.00 |
| RC13 | CV | 20666.99 (optimal, 36.95 s) | incumbent **19938.07** (EV ile birebir aynı), 300 s'de gap **%8,7** — henüz kanıtlanmadı |

**§4'ün İLK YAZIMINDAKİ İDDİA YANLIŞTI ve BURADA DÜZELTİLİYOR** (CLAUDE.md
Hard Rule §7.4 — hiçbir şey silinmedi, madde 3 aşağıda korunuyor): "RC13/
RC15'in kanıtlanmış optimalleri bu düzeltmeden etkilenmez" iddiası
**ampirik olarak çürütüldü**. Teorik gerekçe (fizibil küme yalnızca
büyür → objektif asla kötüleşmez) **doğruydu ve doğrulandı** — ama
"kötüleşmez" ile "değişmez" aynı şey değildir; C5 gibi küçük/basit
örneklerde objektif gerçekten sabit kalırken, RC13/RC15 gibi TÜM
becerilerin (dolayısıyla önceden atıl kalan TECH_002/004/006'nın) devreye
girdiği örneklerde önceki "optimal" değerler aslında **yanlış girdiyle
(5 teknisyen) kanıtlanmış yanlış optimallerdi** — gerçek problem (8
teknisyen) daha ucuza çözülebiliyormuş. **Makale/rapor için sonuç: RC13
ve RC15'in daha önce kaydedilen 20666.99 / 23912.82 değerleri artık
GEÇERSİZDİR, yerine 19938.07 / 21851.58 kullanılmalıdır** — ayrıntı ve
kaynak sayfalarındaki güncelleme notları için bkz.
[[karar_rc13_tam_paket_uygulamasi]] ve [[karar_rc13_asgari_paket_uygulamasi]].

**Süre etkisi:** çözüm süreleri de arttı (RC13 EV 5.96s→12.87s, RC15 EV
11.35s→32.15s, RC13 CV 36.95s'de optimal → 300s'de hâlâ %8,7 gap) — beklenen
bir yan etki, çünkü aktif ekip/kombinasyon sayısı (`|T|`) yaklaşık 2,4×
büyüdü (RC20 için ölçülen 15→36 oranıyla tutarlı, bkz.
[[sorun_rc20_darbogaz_kok_neden_analizi]] §5 Ö-A). C5/R5/RC5 gibi küçük
örneklerde bu etki gözlenmedi (hâlâ ~anlık).

## 5. RC20 üzerindeki etki (ölçülmüş ama bu turda İZLENMEDİ/kullanılmadı)

[[sorun_rc20_darbogaz_kok_neden_analizi]] §5 bu tam düzeltmeyi ("Ö-A")
önceden ölçmüştü: RC20 EV'yi INFEASIBLE'dan **fizibil**'e taşıyor
(`|T|` 15→36), ama tam modelde 900 s'de **hâlâ 0 çözüm** veriyor (model
2,4× büyüdüğü için pratik çözülebilirlik kazanılmıyor, alt sınır
20852.6'da kalıyor). Eren'in açık talimatıyla **RC20 üzerinde bu turda
hiçbir ek işlem yapılmadı** (Ö-B/Ö-C/Ö-D dahil) — bu madde yalnızca
kayıt amaçlıdır, ileride RC20'ye dönüldüğünde başlangıç noktasının
değiştiğini hatırlatır.

## Sources

- `raw/CV_model_gurobi_exact.py:~1085-1092` (düzeltilmiş blok)
- `raw/EV_v.1.1.py:~1186-1193` (düzeltilmiş blok)
- `raw/Info4Employee.xml` (8 teknisyen, 5 beceri)
- [[sorun_rc20_darbogaz_kok_neden_analizi]] §2-1, §5 (Ö-A)

## Related

- [[sorun_rc20_darbogaz_kok_neden_analizi]] (bu kararın düzelttiği hatanın teşhisi ve Ö-A'nın önceki ölçümü)
- [[karar_dinamik_teknisyen_ekibi_itertools_combinations]] (`[0]` seçiminin ilk belgelendiği yer)
- [[karar_rc13_tam_paket_uygulamasi]], [[karar_rc13_asgari_paket_uygulamasi]] (bu düzeltmeden etkilenmediği doğrulanan RC13/RC15 sonuçları)
- [[uyumluluk_matrisi]]
